import os
import requests
import msal
import tempfile

# Identifiants Azure AD - Load from environment variables
CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
TENANT_ID = os.getenv("TENANT_ID", "")

# Infos SharePoint - Load from environment variables
SITE_ID = os.getenv("SITE_ID", "studysuccess.sharepoint.com,9e9e1ce0-5693-4484-abdb-6c7c1f350351,3daa2958-c7e0-40f1-a80c-0b19460aa66d")
DRIVE_ID = os.getenv("DRIVE_ID", "b!4ByenpNWhESr22x8HzUDUVgpqj3gx_FAqAwLGUYKpm1hWqPgcevxSoDhcRMK8Na3")

# Scope pour Graph
SCOPES = ["https://graph.microsoft.com/.default"]

# Authentification MSAL
app = msal.ConfidentialClientApplication(
    client_id=CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority=f"https://login.microsoftonline.com/{TENANT_ID}"
)

def get_access_token():
    """Obtient un token d'accès Microsoft Graph"""
    try:
        result = app.acquire_token_for_client(scopes=SCOPES)
        if "access_token" in result:
            return result["access_token"]
        else:
            print(f"Erreur d'authentification: {result.get('error_description', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"Erreur lors de l'acquisition du token: {e}")
        return None

def download_sharepoint_file(file_path: str) -> str:
    """Télécharge un fichier depuis SharePoint"""
    try:
        token = get_access_token()
        if not token:
            print("Impossible d'obtenir le token d'accès")
            return None
        
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://graph.microsoft.com/v1.0/sites/{SITE_ID}/drive/root:/{file_path}:/content"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # Crée un fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                tmp.write(response.content)
                return tmp.name
        else:
            print(f"Erreur lors du téléchargement: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Erreur: {e}")
        return None
