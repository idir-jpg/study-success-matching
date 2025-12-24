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

# Charger les données avec fallback
temp_folder = tempfile.mkdtemp()
mandat_pdf_path = None
pptx_file_path = None
excel_file_path = None
profs_file_path = None

try:
    mandat_pdf_path = download_file("GESTION QUOTIDIENNE/DOCUMENTS UTILES/Mandats/Mandat Study Success_ Particulier Employeur.pdf", ".pdf")
    pptx_file_path = download_file("GESTION QUOTIDIENNE/TEST DE MEMOIRE/testNouveau_Résultat-test.pptx", ".pptx")
    excel_file_path = download_file("GESTION QUOTIDIENNE/Parent_Eleve_Prof.xlsx", ".xlsx")
    profs_file_path = download_file("GESTION QUOTIDIENNE/SCOPE PROFS/Contact_Profs.xlsx", ".xlsx")
    
    if profs_file_path:
        df_profs = pd.read_excel(profs_file_path, sheet_name='Liste profs', usecols=[
            "Nom", "Prénom", "Mail", "Numéro", "Niveau", "Matière", "Actif",
            "Précisions sur la situation", "adresse", "Présentiel ou Visio ?"
        ])
    else:
        raise ValueError("Impossible de charger le fichier des professeurs")
        
    df_profs['Nom'] = df_profs['Nom'].fillna('').astype(str)
    df_profs['Prénom'] = df_profs['Prénom'].fillna('').astype(str)
    
    if excel_file_path:
        sheets = pd.read_excel(excel_file_path, sheet_name=None)
        df_suivi = sheets['Suivi'][[
            'Id', 'Nom', 'Prénom', 'Adresse', 'Niveau', 'Matières enseignées', 'Visio ?',
            "Dispo & Profil de l'élève", "Téléphone parents", "Mail", "Etat", "Professeur", "Gérant", "Tps attente"
        ]].copy()
    else:
        raise ValueError("Impossible de charger le fichier de suivi")
        
    df_suivi['Etat'] = df_suivi['Etat'].fillna('')
    df_suivi = df_suivi[df_suivi['Etat'].astype(str).str.strip().str.match(r'^[0-2]')]
    df_suivi['Nom'] = df_suivi['Nom'].str.upper()

except Exception as e:
    st.warning(f"⚠️ Impossible de charger les données SharePoint: {e}")
    st.info("💡 Mode demo activé - Les données ne sont pas disponibles. Veuillez vérifier la configuration.")
    
    # Créer des données fictives pour demo
    df_profs = pd.DataFrame({
        "Nom": ["DUPONT", "MARTIN"],
        "Prénom": ["Jean", "Marie"],
        "Mail": ["jean.dupont@email.com", "marie.martin@email.com"],
        "Numéro": ["0123456789", "0987654321"],
        "Niveau": ["Collège", "Lycée"],
        "Matière": ["Mathématiques", "Français"],
        "Actif": ["Oui", "Oui"],
        "Précisions sur la situation": ["", ""],
        "adresse": ["Paris", "Lyon"],
        "Présentiel ou Visio ?": ["Présential", "Visio"]
    })
    
    df_suivi = pd.DataFrame({
        "Id": [1, 2],
        "Nom": ["DUPONT", "MARTIN"],
        "Prénom": ["Pierre", "Sophie"],
        "Adresse": ["Paris", "Lyon"],
        "Niveau": ["Collège", "Lycée"],
        "Matières enseignées": ["Mathématiques", "Français"],
        "Visio ?": ["Oui", "Non"],
        "Dispo & Profil de l'élève": ["Flexible", "Flexible"],
        "Téléphone parents": ["0123456789", "0987654321"],
        "Mail": ["pierre.dupont@email.com", "sophie.martin@email.com"],
        "Etat": ["1", "2"],
        "Professeur": ["", ""],
        "Gérant": ["", ""],
        "Tps attente": ["", ""]
    })

st.header("1️⃣ Rechercher un élève")
prenom_input = st.text_input("Prénom")
nom_input = st.text_input("Nom (en MAJUSCULES)")

resultats = df_suivi.copy()
if prenom_input:
    resultats = resultats[resultats['Prénom'].str.lower().str.contains(prenom_input.lower())]
if nom_input:
    resultats = resultats[resultats['Nom'].str.upper().str.contains(nom_input.upper())]

if not resultats.empty:
    st.dataframe(resultats, use_container_width=True)
    selected_row = st.selectbox("Sélectionner un élève", range(len(resultats)), format_func=lambda x: f"{resultats.iloc[x]['Prénom']} {resultats.iloc[x]['Nom']}")
    
    eleve_info = resultats.iloc[selected_row]
    st.subheader(f"✅ Élève sélectionné: {eleve_info['Prénom']} {eleve_info['Nom']}")
else:
    st.info("Aucun résultat trouvé")

st.header("2️⃣ Rechercher un professeur")
profs_niveau = st.multiselect("Niveau(x):", df_profs['Niveau'].unique())
profs_matiere = st.multiselect("Matière(s):", df_profs['Matière'].unique())

profs_filtrés = df_profs.copy()
if profs_niveau:
    profs_filtrés = profs_filtrés[profs_filtrés['Niveau'].isin(profs_niveau)]
if profs_matiere:
    profs_filtrés = profs_filtrés[profs_filtrés['Matière'].isin(profs_matiere)]

if not profs_filtrés.empty:
    st.dataframe(profs_filtrés, use_container_width=True)
    selected_prof = st.selectbox("Sélectionner un professeur", range(len(profs_filtrés)), format_func=lambda x: f"{profs_filtrés.iloc[x]['Prénom']} {profs_filtrés.iloc[x]['Nom']}")
    
    prof_info = profs_filtrés.iloc[selected_prof]
    st.subheader(f"✅ Professeur sélectionné: {prof_info['Prénom']} {prof_info['Nom']}")
else:
    st.info("Aucun professeur trouvé avec ces critères")

st.header("3️⃣ Prévisualiser et envoyer un email")
if 'eleve_info' in locals() and 'prof_info' in locals():
    email_html = generate_email_html(eleve_info, prof_info)
    st.markdown(email_html, unsafe_allow_html=True)
    
    if st.button("📧 Envoyer l'email"):
        try:
            send_mail(prof_info['Mail'], eleve_info['Mail'], email_html, selected_sender, mode_test)
            st.success("✅ Email envoyé avec succès!")
        except Exception as e:
            st.error(f"❌ Erreur lors de l'envoi: {e}")
else:
    st.info("Sélectionnez d'abord un élève et un professeur")
