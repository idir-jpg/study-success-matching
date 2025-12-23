# matching_eml.py
import os
import datetime as dt
import numpy as np
import pandas as pd
from email.message import EmailMessage
from email.utils import make_msgid

# googlemaps est optionnel : on ne bloque pas si non installé
try:
    import googlemaps
except Exception:
    googlemaps = None


def _next_departure_18h() -> dt.datetime:
    now = dt.datetime.now()
    wd = now.weekday()  # 0=Mon ... 6=Sun
    if wd in (0, 1, 2, 3, 6):  # Lun, Mar, Mer, Jeu, Dim -> demain 18h
        target = now + dt.timedelta(days=1)
    else:  # Ven / Sam -> lundi 18h
        delta = (7 - wd) % 7 or 7
        target = now + dt.timedelta(days=delta)
    return dt.datetime(target.year, target.month, target.day, 18, 0)


def _calc_duration_minutes(gmaps_client, source: str, destination: str):
    try:
        if not source or not destination:
            return None
        directions = gmaps_client.directions(
            origin=str(source),
            destination=str(destination),
            mode="transit",
            departure_time=_next_departure_18h(),
        )
        if directions:
            leg = directions[0]["legs"][0]
            return int(leg["duration"]["value"] // 60)
    except Exception:
        return None
    return None


def _format_matieres(matieres_str: str) -> str:
    s = str(matieres_str).replace("[", "").replace("]", "").replace('"', "").replace("'", "").strip()
    parts = [m.strip() for m in s.split(";") if m.strip()]
    if len(parts) > 1:
        return ", ".join(parts[:-1]) + " et " + parts[-1]
    return parts[0] if parts else ""


def _build_emltpl(subject: str, html_body: str, bcc_list=None, to_list=None, cc_list=None) -> bytes:
    bcc_list = bcc_list or []
    to_list = to_list or []
    cc_list = cc_list or []

    msg = EmailMessage()
    msg["Subject"] = subject
    if to_list:
        msg["To"] = ", ".join([e for e in to_list if e])
    if cc_list:
        msg["Cc"] = ", ".join([e for e in cc_list if e])
    if bcc_list:
        # .emltpl conservera les Bcc dans l’entête ; les clients Apple savent l’ouvrir.
        msg["Bcc"] = ", ".join([e for e in bcc_list if e])

    msg["Message-ID"] = make_msgid()
    msg["X-Priority"] = "3"
    msg.set_content("Version texte : ce message contient un corps HTML.")
    msg.add_alternative(html_body, subtype="html")
    return msg.as_bytes()


def run_matching(selected_row: pd.Series,
                 sheets: dict,
                 df_profs: pd.DataFrame,
                 selected_emails=None,
                 google_api_key: str | None = None):
    """
    - Sans `selected_emails` : retourne le DataFrame des profs proposés trié par 'Durée Transport (min)'.
    - Avec  `selected_emails` : retourne (file_name, eml_bytes).

    `google_api_key` :
      - passe la clé directement (recommandé via st.secrets)
      - sinon lue dans l'env: GOOGLE_API_KEY
    """
    try:
        # ---- Déduction niveau / matières / visio ----
        niveau_raw = str(selected_row.get("Niveau", "")).strip().lower()
        matieres_str = str(selected_row.get("Matières enseignées", ""))
        visio = str(selected_row.get("Visio ?", "")).strip().lower() == "visio"

        niveau_map = {
            "primaire": "primaire",
            "6e": "collège", "5e": "collège", "4e": "collège", "3e": "collège",
            "seconde": "lycée", "première": "lycée", "terminale": "lycée",
        }
        niveau_eleve = niveau_map.get(niveau_raw, "supérieur")

        mats = []
        low = matieres_str.lower()
        if "maths" in low: mats.append("maths")
        if "physique" in low: mats.append("physique")
        if "svt" in low or "biologie" in low: mats.append("svt")
        if "informatique" in low: mats.append("informatique")
        if not mats:
            return pd.DataFrame() if selected_emails is None else ("", b"")

        # ---- Filtres profs (identiques à ta version) ----
        df = df_profs.copy()
        if visio:
            df = df[df["Présentiel ou Visio ?"].str.lower().str.contains("visio", na=False)]
        else:
            df = df[df["Présentiel ou Visio ?"].str.lower() != "visio"]

        df = df[df["Actif"].isin(["2.Prof OK", "4.Prof potentiellement OK"])]
        df = df[df["Niveau"].str.contains(niveau_eleve, case=False, na=False)]

        # matières
        mats_regex = "|".join(mats)
        df = df[df["Matière"].str.lower().str.contains(mats_regex, na=False)]

        # ---- Durée transport (présentiel + clé) ----
        df["Durée Transport (min)"] = np.nan
        origine = str(selected_row.get("Adresse", "")).strip()

        # détecter la colonne d'adresse prof (la plus “complète”)
        adresse_prof_col = None
        candidates = [c for c in df.columns if "adresse" in c.lower()]
        # privilégier une colonne qui n'a pas "code postal" dans le nom si dispo
        for c in candidates:
            if "code" not in c.lower():
                adresse_prof_col = c
                break
        if not adresse_prof_col and candidates:
            adresse_prof_col = candidates[0]  # à défaut

        # clé : param > env
        api_key = google_api_key or os.getenv("GOOGLE_API_KEY", "")

        if not visio and api_key and googlemaps and adresse_prof_col and origine:
            try:
                gmaps = googlemaps.Client(key=api_key)
                df["Durée Transport (min)"] = df[adresse_prof_col].apply(
                    lambda dest: _calc_duration_minutes(gmaps, origine, dest)
                )
            except Exception:
                pass  # on laisse à NaN si l’API plante

        # ---- Tri (NaN en bas) ----
        df["_dur_tri"] = df["Durée Transport (min)"].fillna(10**9)
        df = df.sort_values("_dur_tri", ascending=True).drop(columns=["_dur_tri"]).reset_index(drop=True)

        if selected_emails is None:
            return df

        # ---- Construction de l'email (.emltpl) ----
        prenom_eleve = selected_row.get("Prénom", "")
        adresse = "Visio" if visio else selected_row.get("Adresse", "")
        dispo = selected_row.get("Dispo & Profil de l'élève", "")
        niveau_aff = selected_row.get("Niveau", "")
        matieres_aff = _format_matieres(selected_row.get("Matières enseignées", ""))

        subject = f"Proposition d'élève - Niveau {niveau_aff} pour des cours de {matieres_aff}"
        html_body = f"""
        <html><body>
        Hello !<br><br>
        C'est Idir de Study Success, j'espère que tu vas bien ! 😊<br>
        Si tu reçois ce mail, c'est parce que tu corresponds parfaitement au profil recherché pour un(e) de nos élèves.<br><br>
        📌 <b>Élève : {prenom_eleve}</b><br>
        • Classe : {niveau_aff}<br>
        • Matière : {matieres_aff}<br>
        • Dispos : {dispo}<br>
        • Adresse : {adresse}<br><br>
        Réponds simplement à ce mail si tu es dispo !<br><br>
        À très vite,<br>Idir
        </body></html>""".strip()

        eml_bytes = _build_emltpl(subject=subject, html_body=html_body, bcc_list=selected_emails)
        file_name = f"Proposition_{prenom_eleve}_{niveau_aff}.emltpl".replace(" ", "_")
        return file_name, eml_bytes

    except Exception as e:
        print(f"[ERREUR MATCHING] {e}")
        return pd.DataFrame() if selected_emails is None else ("", b"")
