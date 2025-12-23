"""
send_mail_streamlit.py
Fonction d'envoi de mail via Office 365 (MSAL) compatible Mac/Windows
Utilise les variables d'environnement pour l'authentification
"""

import os
import requests
import base64
from msal import ConfidentialClientApplication
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration MSAL (Microsoft Authentication Library)
TENANT_ID = os.environ.get("TENANT_ID")
CLIENT_ID = os.environ.get("CLIENT_ID")
CERT_THUMBPRINT = os.environ.get("CERT_THUMBPRINT")

# Lire le certificat depuis variable d'environnement OU fichier
if "CERT_PRIVATE_KEY" in os.environ:
    PRIVATE_KEY = os.environ["CERT_PRIVATE_KEY"]
else:
    CERT_PRIVATE_KEY_PATH = os.environ.get("CERT_PRIVATE_KEY_PATH", "mailer.key")
    try:
        with open(CERT_PRIVATE_KEY_PATH, "r") as f:
            PRIVATE_KEY = f.read()
    except FileNotFoundError:
        PRIVATE_KEY = None

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]

# Configuration des expéditeurs
SENDERS = {
    "idir.hadjhamou@study-success.fr": "Idir HADJ HAMOU",
    "manon.curie@study-success.fr": "Manon CURIE",
    "lucas.ledanois@study-success.fr": "Lucas LE DANOIS",
    "mathilde.boher@study-success.fr": "Agathe BOHER",
}

# Instance MSAL
app = None
if TENANT_ID and CLIENT_ID and PRIVATE_KEY and CERT_THUMBPRINT:
    try:
        app = ConfidentialClientApplication(
            client_id=CLIENT_ID,
            authority=AUTHORITY,
            client_credential={
                "private_key": PRIVATE_KEY,
                "thumbprint": CERT_THUMBPRINT,
            },
        )
    except Exception as e:
        print(f"⚠️ Erreur MSAL: {e}")
        app = None


def get_token():
    """Récupère un token d'accès Microsoft Graph"""
    if not app:
        return None
    
    try:
        result = app.acquire_token_for_client(scopes=SCOPE)
        if "access_token" not in result:
            return None
        return result["access_token"]
    except Exception as e:
        print(f"❌ Erreur authentification: {e}")
        return None


def send_mail(to_email, subject, html_body, from_email, cc=None, bcc=None, attachments=None):
    """
    Envoie un email via Microsoft Graph API
    
    Args:
        to_email (str): Email destinataire
        subject (str): Sujet du mail
        html_body (str): Corps du mail en HTML
        from_email (str): Email expéditeur (doit être dans SENDERS)
        cc (str ou list): Email(s) en copie conforme
        bcc (str ou list): Email(s) en copie cachée
        attachments (list): Liste de tuples (nom_fichier, contenu_bytes)
    
    Returns:
        dict: {"success": True/False, "message": str}
    """
    
    if from_email not in SENDERS:
        return {
            "success": False,
            "message": f"❌ Expéditeur non reconnu: {from_email}"
        }
    
    token = get_token()
    if not token:
        return {
            "success": False,
            "message": "❌ Impossible d'obtenir un token d'authentification\nVérifiez les variables d'environnement: TENANT_ID, CLIENT_ID, CERT_THUMBPRINT"
        }
    
    try:
        # Préparer les destinataires
        to_recipients = [{"emailAddress": {"address": to_email}}]
        cc_recipients = []
        bcc_recipients = []
        
        if cc:
            if isinstance(cc, list):
                cc_recipients = [{"emailAddress": {"address": email}} for email in cc]
            else:
                cc_recipients = [{"emailAddress": {"address": cc}}]
        
        if bcc:
            if isinstance(bcc, list):
                bcc_recipients = [{"emailAddress": {"address": email}} for email in bcc]
            else:
                bcc_recipients = [{"emailAddress": {"address": bcc}}]
        
        # Construire le payload
        message = {
            "subject": subject,
            "bodyPreview": subject,
            "body": {
                "contentType": "HTML",
                "content": html_body
            },
            "toRecipients": to_recipients,
            "ccRecipients": cc_recipients,
            "bccRecipients": bcc_recipients,
        }
        
        # Ajouter les attachments s'il y en a
        if attachments:
            message["attachments"] = []
            for filename, file_content in attachments:
                # Convertir le contenu en base64
                encoded_content = base64.b64encode(file_content).decode('utf-8')
                message["attachments"].append({
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": filename,
                    "contentBytes": encoded_content
                })
        
        # URL Microsoft Graph pour envoyer depuis le compte
        url = f"https://graph.microsoft.com/v1.0/users/{from_email}/sendMail"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "message": message,
            "saveToSentItems": True
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code in [200, 202]:
            return {
                "success": True,
                "message": f"✅ Email envoyé avec succès de {SENDERS[from_email]} vers {to_email}"
            }
        else:
            return {
                "success": False,
                "message": f"❌ Erreur Microsoft Graph ({response.status_code}): {response.text}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Erreur lors de l'envoi: {str(e)}"
        }


def get_sender_list():
    """Retourne la liste des expéditeurs disponibles"""
    return list(SENDERS.keys())


def get_sender_name(email):
    """Retourne le nom de l'expéditeur"""
    return SENDERS.get(email, email)
