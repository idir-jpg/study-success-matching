import os
import requests
import msal
import tempfile
import json
from pathlib import Path

# Identifiants Azure AD - Load from environment variables
CLIENT_ID = os.getenv("CLIENT_ID", "")
TENANT_ID = os.getenv("TENANT_ID", "")

# Essayer plusieurs approches d'authentification
CERT_THUMBPRINT = os.getenv("CERT_THUMBPRINT", "")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")

# Infos SharePoint - Load from environment variables
SITE_ID = os.getenv("SITE_ID", "studysuccess.sharepoint.com,9e9e1ce0-5693-4484-abdb-6c7c1f350351,3daa2958-c7e0-40f1-a80c-0b19460aa66d")
DRIVE_ID = os.getenv("DRIVE_ID", "b!4ByenpNWhESr22x8HzUDUVgpqj3gx_FAqAwLGUYKpm1hWqPgcevxSoDhcRMK8Na3")

# Scope pour Graph
SCOPES = ["https://graph.microsoft.com/.default"]

# Authentification MSAL - Avec certificat ou secret
def create_msal_app():
    """Crée une app MSAL avec certificat ou secret"""
    
    # Tenter avec certificat d'abord
    if PRIVATE_KEY and CERT_THUMBPRINT:
        try:
            # Créer un fichier temporaire pour le certificat
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as f:
                f.write(PRIVATE_KEY)
                cert_path = f.name
            
            print(f"[DEBUG] Utilisation du certificat: {cert_path}")
            
            app = msal.ConfidentialClientApplication(
                client_id=CLIENT_ID,
                authority=f"https://login.microsoftonline.com/{TENANT_ID}",
                client_credential={
                    "thumbprint": CERT_THUMBPRINT,
                    "private_key": PRIVATE_KEY
                }
            )
            print("[DEBUG] App créée avec certificat")
            return app
        except Exception as e:
            print(f"[DEBUG] Erreur avec certificat: {e}")
    
    # Fallback sur secret si disponible
    if CLIENT_SECRET:
        try:
            print("[DEBUG] Utilisation du CLIENT_SECRET")
            app = msal.ConfidentialClientApplication(
                client_id=CLIENT_ID,
                client_credential=CLIENT_SECRET,
                authority=f"https://login.microsoftonline.com/{TENANT_ID}"
            )
            print("[DEBUG] App créée avec secret")
            return app
        except Exception as e:
            print(f"[DEBUG] Erreur avec secret: {e}")
    
    # Si rien ne fonctionne, retourner None
    print("[DEBUG] Impossible de créer une app MSAL")
    return None

app = create_msal_app()

def get_access_token():
    """Obtient un token d'accès Microsoft Graph"""
    try:
        if not app:
            print("❌ App MSAL non initialisée")
            return None
            
        result = app.acquire_token_for_client(scopes=SCOPES)
        if "access_token" in result:
            print("✅ Token obtenu avec succès")
            return result["access_token"]
        else:
            print(f"❌ Erreur d'authentification: {result.get('error_description', 'Unknown error')}")
            print(f"[DEBUG] Full response: {result}")
            return None
    except Exception as e:
        print(f"❌ Erreur lors de l'acquisition du token: {e}")
        return None

def download_sharepoint_file(file_path: str, suffix: str = ".xlsx") -> str:
    """Télécharge un fichier depuis SharePoint"""
    try:
        token = get_access_token()
        if not token:
            print("❌ Impossible d'obtenir le token d'accès")
            return None
        
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://graph.microsoft.com/v1.0/sites/{SITE_ID}/drive/root:/{file_path}:/content"
        
        print(f"📥 Téléchargement: {file_path}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # Crée un fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(response.content)
                print(f"✅ Fichier téléchargé: {tmp.name}")
                return tmp.name
        else:
            print(f"❌ Erreur lors du téléchargement: {response.status_code}")
            print(f"[DEBUG] Response: {response.text[:500]}")
            return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

# Alias pour compatibilité
def download_file(file_path: str, suffix: str = ".xlsx") -> str:
    """Alias pour download_sharepoint_file"""
    return download_sharepoint_file(file_path, suffix)
