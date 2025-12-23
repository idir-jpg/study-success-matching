# email_prof_eml.py

import os
import tempfile
import pandas as pd
import base64
from email.message import EmailMessage


def get_signature_html(sender_email):
    """
    Retourne le HTML de la signature avec l'image encodée en base64
    """
    if not sender_email:
        return ""
    
    # Déterminer le fichier de signature
    email_prefix = sender_email.split('.')[0].lower()
    signature_map = {
        "idir": "Signature_idir.png",
        "manon": "Signature_manon.png",
        "lucas": "Signature_lucas.png",
        "mathilde": "Signature_mathilde.png",
    }
    
    signature_file = signature_map.get(email_prefix, "")
    
    # Si le fichier existe, l'encoder en base64
    if signature_file and os.path.exists(signature_file):
        try:
            with open(signature_file, "rb") as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
            # Retourner une image encodée en base64 intégrée avec tirets avant
            return f"""--<br><img src="data:image/png;base64,{img_data}" style="max-width: 350px; margin-top: 10px;" alt="Signature">"""
        except Exception as e:
            print(f"Erreur lecture signature {signature_file}: {e}")
            return ""
    
    return ""


def generate_email_html(selected_row, df_profs, selected_prof, sender_email=None):
    """
    Génère le contenu HTML d'un email pour contacter un professeur
    Retourne un dictionnaire avec les infos nécessaires pour envoyer le mail
    
    Args:
        selected_row: Données de l'élève (pandas Series)
        df_profs: DataFrame des professeurs
        selected_prof: Données du professeur sélectionné (pandas Series)
        sender_email: Email du sender (pour ajouter la bonne signature)
    
    Returns:
        dict avec subject, html_body, to_email, cc_email, prof_name
        ou None si erreur
    """
    try:
        # Récupérer les emails
        prof_email = selected_prof.get('Mail', 'N/A')
        parent_email = selected_row.get('Mail', 'N/A')
        
        # Vérifier si Visio ou adresse physique
        is_visio = selected_row.get('Visio ?', 'Non').lower() in ['oui', 'visio']
        adresse = 'Visio' if is_visio else selected_prof.get('adresse', 'Adresse non disponible')
        
        # Obtenir la signature en base64
        signature_html = get_signature_html(sender_email)

        # Corps du message HTML
        html_body = f"""<html><body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <p>Bonjour !<br><br>
    Comme convenu, voici toutes les informations pour organiser le premier cours d'essai avec {selected_row.get('Prénom', 'N/A')} :<br><br></p>
    
    <p><b>📌 Informations de l'élève</b><br>
    • Prénom & Nom : {selected_row.get('Prénom', 'N/A')} {selected_row.get('Nom', 'N/A')}<br>
    • Classe : {selected_row.get('Niveau', 'N/A')}<br>
    • Dispo et profil de l'élève : {selected_row.get("Dispo & Profil de l'élève", 'N/A')}<br>
    • Numéro de contact : {selected_row.get('Téléphone parents', 'N/A')}<br>
    • Adresse : {adresse}<br><br></p>
    
    <p><b>📌 Coordonnées du professeur</b><br>
    • Nom du professeur : {selected_prof.get('Prénom', 'N/A')} {selected_prof.get('Nom', 'N/A')}<br>
    • Numéro de téléphone : {selected_prof.get('Numéro', 'N/A')}<br>
    • Adresse e-mail : {selected_prof.get('Mail', 'N/A')}<br><br></p>
    
    <p><b>📌 Organisation du premier échange</b><br>
    {selected_prof.get('Prénom', 'Professeur')}, je t'invite à contacter la famille afin de convenir ensemble d'un créneau pour le premier cours. Une fois l'échange téléphonique fait, merci de m'envoyer un SMS ou un mail pour me confirmer la date et l'heure du cours.<br><br></p>
    
    <p><b>📌 Rappels importants</b><br>
    • Le cours d'essai ne doit pas excéder 1h.<br>
    • Après ce premier cours, nous allons vous contacter pour un rapide point par téléphone afin d'échanger sur ce cours d'essai.<br><br></p>
    
    <p>N'hésitez surtout pas à me solliciter pour toute question.<br><br>
    A très bientôt !<br><br>
    {signature_html}</p>
</body></html>"""

        return {
            "subject": f"Coordonnées Elèves: {selected_row.get('Prénom', 'N/A')} {selected_row.get('Nom', 'N/A')}",
            "html_body": html_body,
            "to_email": prof_email,
            "cc_email": parent_email,
            "prof_name": f"{selected_prof.get('Prénom', 'N/A')} {selected_prof.get('Nom', 'N/A')}",
            "sender_email": sender_email
        }

    except Exception as e:
        print(f"Erreur dans generate_email_html: {e}")
        return None


def generate_email(selected_row, excel_file_path, pdf_file_path, df_profs):
    # Lecture du fichier Excel
    df = pd.read_excel(excel_file_path, sheet_name=None)
    selected_id = selected_row['Id']

    # Récupération des infos élève
    details_df = df['Profils_élèves'].loc[df['Profils_élèves']['id'] == selected_id]
    if details_df.empty:
        print(f"Aucun élève trouvé avec l'ID {selected_id}.")
        return None
    details = details_df.iloc[0]

    suivi_info = df['Suivi'].loc[df['Suivi']['Id'] == selected_id].iloc[0]
    parent_email = suivi_info['Mail']

    # Chemin vers le PDF
    pdf_file_name = f"{details['Prénom']} résultat profil d'apprentissage.pdf"
    pdf_path = os.path.join(pdf_file_path, pdf_file_name)

    # Récupération du professeur
    nom_input = selected_row.get('Nom_prof', '')
    prenom_input = selected_row.get('Prenom_prof', '')

    profs = df_profs[
        (df_profs['Nom'].str.contains(nom_input, case=False, na=False)) &
        (df_profs['Prénom'].str.contains(prenom_input, case=False, na=False))
    ]

    if profs.empty:
        print("Aucun prof trouvé. Email non généré.")
        return None

    selected_prof = profs.iloc[0]
    prof_email = selected_prof['Mail']

    adresse = selected_row['Adresse'] if selected_row['Visio ?'].lower() != 'visio' else 'Visio'

    # Corps du message HTML
    html_body = f"""<html><body>
    Bonjour !<br><br>
    Comme convenu, voici toutes les informations pour organiser le premier cours d'essai avec {selected_row['Prénom']} :<br><br>
    
    <b>📌 Informations de l'élève</b><br>
    • Prénom & Nom : {selected_row['Prénom']} {selected_row['Nom']}<br>
    • Classe : {selected_row['Niveau']}<br>
    • Dispo et profil de l'élève : {selected_row["Dispo & Profil de l'élève"]}<br>
    • Numéro de contact : {selected_row['Téléphone parents']}<br>
    • Adresse : {adresse}<br><br>
    
    <b>📌 Coordonnées du professeur</b><br>
    • Nom du professeur : {selected_prof['Prénom']} {selected_prof['Nom']}<br>
    • Numéro de téléphone : {selected_prof['Numéro']}<br>
    • Adresse e-mail : {selected_prof['Mail']}<br><br>
    
    <b>📌 Organisation du premier échange</b><br>
    {selected_prof['Prénom']}, je t'invite à contacter la famille afin de convenir ensemble d'un créneau pour le premier cours. Une fois l'échange téléphonique fait, merci de m'envoyer un SMS ou un mail pour me confirmer la date et l'heure du cours.<br><br>
    
    <b>📌 Rappels importants</b><br>
    • Le cours d'essai ne doit pas excéder 1h.<br>
    • Après ce premier cours, nous allons vous contacter pour un rapide point par téléphone afin d'échanger sur ce cours d'essai.<br><br>
    
    N'hésitez surtout pas à me solliciter pour toute question.<br><br>
    A très bientôt !
    </body></html>"""

    # Création de l'email
    msg = EmailMessage()
    msg['Subject'] = f"Coordonnées Elèves: {selected_row['Prénom']} {selected_row['Nom']}"
    msg['To'] = prof_email
    msg['Cc'] = parent_email
    msg['Bcc'] = ''
    msg.set_content("Ce message contient un contenu HTML.")
    msg.add_alternative(html_body, subtype='html')

    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            msg.add_attachment(
                f.read(),
                maintype='application',
                subtype='pdf',
                filename=os.path.basename(pdf_path)
            )

    # Sauvegarde au format .emltpl
    temp_eml_path = os.path.join(tempfile.gettempdir(), "email_coordonnees_prof.emltpl")
    with open(temp_eml_path, "wb") as f:
        f.write(bytes(msg))

    print("✅ Fichier .emltpl généré !")
    return temp_eml_path
