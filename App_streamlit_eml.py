import streamlit as st
import pandas as pd
import os
import tempfile
import warnings
from email_prof_eml import generate_email, generate_email_html
from send_mail_streamlit import send_mail, get_sender_list, get_sender_name
from Graph_Api import download_file
from mandat import generate_mandat_email

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

st.set_page_config(page_title="Matching Elève-Prof", layout="wide")
st.title("🧑‍🏫 Interface Matching Elève / Professeur")

# ============ CONFIGURATION GLOBALE ============
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    st.write("")  # Espacement
with col2:
    sender_options = get_sender_list()
    selected_sender = st.radio(
        "📧 Sender par défaut :",
        sender_options,
        format_func=lambda x: get_sender_name(x),
        horizontal=True,
        key="global_sender"
    )
with col3:
    mode_test = st.checkbox("🧪 Mode Test", value=False)
    if mode_test:
        st.warning("⚠️ Mode TEST activé - Les emails seront envoyés à idir.hadjhamou@study-success.fr")

st.markdown("---")

try:
    temp_folder = tempfile.mkdtemp()
    mandat_pdf_path = download_file("GESTION QUOTIDIENNE/DOCUMENTS UTILES/Mandats/Mandat Study Success_ Particulier Employeur.pdf", ".pdf")
    pptx_file_path = download_file("GESTION QUOTIDIENNE/TEST DE MEMOIRE/testNouveau_Résultat-test.pptx", ".pptx")
    excel_file_path = download_file("GESTION QUOTIDIENNE/Parent_Eleve_Prof.xlsx", ".xlsx")
    profs_file_path = download_file("GESTION QUOTIDIENNE/SCOPE PROFS/Contact_Profs.xlsx", ".xlsx")
    df_profs = pd.read_excel(profs_file_path, sheet_name='Liste profs', usecols=[
        "Nom", "Prénom", "Mail", "Numéro", "Niveau", "Matière", "Actif",
        "Précisions sur la situation", "adresse", "Présentiel ou Visio ?"
    ])
    df_profs['Nom'] = df_profs['Nom'].fillna('').astype(str)
    df_profs['Prénom'] = df_profs['Prénom'].fillna('').astype(str)
    sheets = pd.read_excel(excel_file_path, sheet_name=None)
    df_suivi = sheets['Suivi'][[
        'Id', 'Nom', 'Prénom', 'Adresse', 'Niveau', 'Matières enseignées', 'Visio ?',
        "Dispo & Profil de l'élève", "Téléphone parents", "Mail", "Etat", "Professeur", "Gérant", "Tps attente"
    ]].copy()
    df_suivi['Etat'] = df_suivi['Etat'].fillna('')
    df_suivi = df_suivi[df_suivi['Etat'].astype(str).str.strip().str.match(r'^[0-2]')]
    df_suivi['Nom'] = df_suivi['Nom'].str.upper()

except Exception as e:
    st.error(f"Erreur de chargement SharePoint : {e}")
    st.stop()

st.header("1️⃣ Rechercher un élève")
prenom_input = st.text_input("Prénom")
nom_input = st.text_input("Nom (en MAJUSCULES)")

resultats = df_suivi.copy()
if prenom_input:
    resultats = resultats[resultats['Prénom'].str.lower().str.contains(prenom_input.lower())]
if nom_input:
    resultats = resultats[resultats['Nom'].str.upper().str.contains(nom_input.upper())]

if st.button("Rechercher") and resultats.empty:
    st.warning("Aucun élève trouvé.")

if not resultats.empty:
    selected_index = st.selectbox(
        "Choisir un élève :",
        resultats.index,
        format_func=lambda i: f"{resultats.at[i, 'Prénom']} {resultats.at[i, 'Nom']} - Gérant : {resultats.at[i, 'Gérant']}"
    )
    selected_row = resultats.loc[selected_index]
    st.session_state.selected_row = selected_row
    
    st.markdown("---")
    st.subheader("🎓 Élève sélectionné")
    st.write(selected_row[['Nom', 'Prénom', 'Adresse', 'Niveau', 'Matières enseignées', 'Visio ?']])
    st.markdown("---")
elif (prenom_input or nom_input) and resultats.empty:
    st.warning("Aucun élève trouvé avec ces critères.")


# ========== OPTION 2 : COORDONNÉES PROF ==========
st.subheader("2️⃣ Envoi des coordonnées prof")

if "selected_row" not in st.session_state:
    st.warning("Veuillez d'abord sélectionner un élève.")
else:
    selected_row = st.session_state.selected_row
    
    prof_firstname = st.text_input("Prénom du professeur")
    prof_lastname = st.text_input("Nom du professeur")
    
    # Recherche en temps réel
    filtered_profs = df_profs.copy()
    
    if prof_firstname:
        filtered_profs = filtered_profs[filtered_profs['Prénom'].str.contains(prof_firstname, case=False, na=False)]
    
    if prof_lastname:
        filtered_profs = filtered_profs[filtered_profs['Nom'].str.contains(prof_lastname, case=False, na=False)]
    
    # Filtre pour les professeurs actifs
    filtered_profs = filtered_profs[filtered_profs['Actif'].notna()]
    
    if len(filtered_profs) > 0:
        selected_prof_index = st.selectbox(
            "Sélectionner un professeur",
            filtered_profs.index,
            format_func=lambda i: f"{filtered_profs.at[i, 'Prénom']} {filtered_profs.at[i, 'Nom']}"
        )
        
        selected_prof = filtered_profs.loc[selected_prof_index]
        
        # Afficher les infos du prof
        st.write("**Informations du professeur :**")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"📧 Email: {selected_prof.get('Mail', 'N/A')}")
            st.write(f"📍 Adresse: {selected_prof.get('adresse', 'N/A')}")
        with col2:
            st.write(f"🎯 Présentiel/Visio: {selected_prof.get('Présentiel ou Visio ?', 'N/A')}")
            st.write(f"📚 Niveau: {selected_prof.get('Niveau', 'N/A')}")
        st.write(f"📖 Matière: {selected_prof.get('Matière', 'N/A')}")
        
        st.markdown("---")
        
        # Bouton aperçu
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("👁️ Aperçu du mail"):
                st.session_state.show_preview = True
        
        with col_btn2:
            if st.button("📧 Envoyer directement"):
                email_data = generate_email_html(selected_row, df_profs, selected_prof, sender_email=selected_sender)
                if email_data:
                    to_email = email_data['to_email']
                    if mode_test:
                        to_email = "idir.hadjhamou@study-success.fr"
                    
                    result = send_mail(
                        to_email=to_email,
                        subject=email_data['subject'],
                        html_body=email_data['html_body'],
                        from_email=selected_sender,
                        cc=email_data['cc_email'] if not mode_test else None
                    )
                    if result["success"]:
                        st.success(f"✅ Email envoyé!")
                    else:
                        st.error(f"❌ Erreur: {result['message']}")
        
        # Aperçu du mail
        if st.session_state.get('show_preview', False):
            email_data = generate_email_html(selected_row, df_profs, selected_prof, sender_email=selected_sender)
            if email_data:
                st.markdown("---")
                st.markdown("### 👁️ Aperçu du mail")
                st.write(f"**De:** {get_sender_name(selected_sender)}")
                st.write(f"**À:** {email_data['to_email']}")
                st.write(f"**Cc:** {email_data['cc_email']}")
                st.write(f"**Sujet:** {email_data['subject']}")
                st.markdown("---")
                st.write(email_data['html_body'], unsafe_allow_html=True)
                st.markdown("---")
                
                col_send1, col_send2 = st.columns(2)
                with col_send1:
                    if st.button("📧 Envoyer"):
                        result = send_mail(
                            to_email=email_data['to_email'] if not mode_test else "idir.hadjhamou@study-success.fr",
                            subject=email_data['subject'],
                            html_body=email_data['html_body'],
                            from_email=selected_sender,
                            cc=email_data['cc_email'] if not mode_test else None
                        )
                        if result["success"]:
                            st.success(f"✅ Email envoyé!")
                            st.session_state.show_preview = False
                        else:
                            st.error(f"❌ Erreur: {result['message']}")
                
                with col_send2:
                    if st.button("❌ Fermer"):
                        st.session_state.show_preview = False

st.markdown("---")

# ========== OPTION 3 : ENVOI DU MANDAT ==========
st.subheader("3️⃣ Envoi du mandat")

if "selected_row" not in st.session_state:
    st.warning("Veuillez d'abord sélectionner un élève.")
else:
    selected_row = st.session_state.selected_row
    
    # Get parent email
    parent_email = selected_row.get('Mail')
    
    if pd.isna(parent_email) or parent_email == '':
        st.error("❌ L'élève sélectionné n'a pas d'email parent enregistré.")
    else:
        st.write(f"📧 **Email du parent :** {parent_email}")
        
        # Send button for mandat (no preview)
        if st.button("📧 Envoyer le mandat", key="send_mandat_btn"):
            try:
                import base64
                from email_prof_eml import get_signature_html
                
                # Get signature using the email_prof_eml function
                signature_html = get_signature_html(selected_sender)
                
                # Fallback: if function doesn't return signature, generate it here
                if not signature_html:
                    email_prefix = selected_sender.split('.')[0].lower()
                    signature_map = {
                        "idir": "Signature_idir.png",
                        "manon": "Signature_manon.png",
                        "lucas": "Signature_lucas.png",
                        "mathilde": "Signature_mathilde.png",
                    }
                    signature_file = signature_map.get(email_prefix, "")
                    if signature_file and os.path.exists(signature_file):
                        try:
                            with open(signature_file, "rb") as f:
                                img_data = base64.b64encode(f.read()).decode('utf-8')
                            signature_html = f'--<br><img src="data:image/png;base64,{img_data}" style="max-width: 350px; margin-top: 10px;" alt="Signature">'
                        except Exception as e:
                            st.warning(f"⚠️ Erreur lecture signature: {e}")
                            signature_html = "--"
                
                # Generate HTML body for mandat email with signature
                html_body = f"""<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <p>Bonjour,</p>
    <p>J'espère que vous allez bien.</p>
    <p>Pour commencer les cours de manière légale, nous avons besoin que vous remplissiez et signiez le mandat ci-joint.</p>
    <p>Comme expliqué, il ne vous engage à rien après cette première heure de cours.</p>
    <p>Bien à vous,</p>
    <br>
    {signature_html}
</body>
</html>"""
                
                # Read and prepare attachment (PDF) from local folder
                attachments = []
                # Look for the PDF in the current directory
                pdf_filename = "Mandat Study Success_ Particulier Employeur.pdf"
                if os.path.exists(pdf_filename):
                    with open(pdf_filename, "rb") as f:
                        attachments.append(("Mandat Study Success.pdf", f.read()))
                    st.info(f"✅ PDF trouvé: {pdf_filename}")
                else:
                    st.warning(f"⚠️ PDF non trouvé: {pdf_filename}")
                
                to_email = parent_email
                subject = "Mandat Study Success"
                
                if mode_test:
                    to_email = "idir.hadjhamou@study-success.fr"
                    subject = f"[TEST] {subject}"
                
                result = send_mail(
                    to_email=to_email,
                    subject=subject,
                    html_body=html_body,
                    from_email=selected_sender,
                    cc=None,
                    attachments=attachments if attachments else None
                )
                
                if result["success"]:
                    st.success(f"✅ Mandat envoyé avec succès à {selected_row['Prénom']} {selected_row['Nom']}!")
                else:
                    st.error(f"❌ Erreur: {result['message']}")
            except Exception as e:
                st.error(f"❌ Erreur lors de l'envoi: {str(e)}")

st.markdown("---")
st.caption("© 2025 Study Success - Interface de matching pédagogique")
