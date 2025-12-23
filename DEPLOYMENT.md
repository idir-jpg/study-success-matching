# 🚀 Guide de déploiement sur Streamlit Cloud

## Étape 1 : Initialiser un repository GitHub

1. Ouvre https://github.com/new
2. Crée un nouveau repository :
   - **Repository name** : `study-success-matching`
   - **Description** : "Interface de matching élève-professeur avec envoi d'emails automatiques"
   - **Public** (pour que Streamlit Cloud puisse l'accéder)
   - Clique "Create repository"

## Étape 2 : Préparer les fichiers localement

Dans le dossier du projet, initialise Git :

```bash
cd '/Users/mac/Library/CloudStorage/OneDrive-Bibliothèquespartagées-StudySuccess/Sharepoint - Study Success - Documents/GESTION QUOTIDIENNE/algo matching/Idir/Algo Houda'

# Initialiser le repository Git
git init

# Ajouter les fichiers (SANS .env et fichiers sensibles)
git add .
git commit -m "Initial commit: Streamlit app for student-professor matching"

# Ajouter le repository GitHub comme remote
git remote add origin https://github.com/hadjhamou/study-success-matching.git

# Pusher sur GitHub
git branch -M main
git push -u origin main
```

## Étape 3 : Configurer Streamlit Cloud

1. Va sur https://share.streamlit.io
2. Clique "New app"
3. Connecte ton compte GitHub (si demandé)
4. Remplis :
   - **Repository** : `hadjhamou/study-success-matching`
   - **Branch** : `main`
   - **Main file path** : `App_streamlit_eml.py`

5. Clique "Deploy"

## Étape 4 : Ajouter les secrets (Variables d'environnement)

1. Dans le dashboard Streamlit Cloud, clique sur l'app
2. Clique sur "Settings" (⚙️)
3. Va dans l'onglet "Secrets"
4. Ajoute tes variables d'environnement (format TOML) :

```toml
TENANT_ID = "51065c1e-192f-467c-be56-f9225e88ebae"
CLIENT_ID = "5ea4abfc-d7f5-41e2-ab5f-f34ef0af8c37"
CERT_THUMBPRINT = "4C1D8CB0300C79139133D72DE4D3336F613ECB5E"
CERT_PRIVATE_KEY_PATH = "mailer.key"
GOOGLE_API_KEY = "AIzaSyCWzjIarEmgkmkiBys5vzkoe0Q1tHiYUnM"
PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
[Contenu complet de ta clé privée]
-----END PRIVATE KEY-----"""
```

## Étape 5 : Tester le déploiement

Une fois déployée, ton app sera accessible à :
**https://study-success-matching.streamlit.app**

## ⚠️ IMPORTANT : Sécurité

**NE JAMAIS** commiter sur GitHub :
- ✗ `.env` file
- ✗ `mailer.key` (fichier de clé privée)
- ✗ Certificats ou secrets

Ces fichiers sont dans `.gitignore` et seront automatiquement ignorés.

## 🔄 Mises à jour futures

Pour déployer des mises à jour :

```bash
# Faire tes modifications localement
# ...

# Committer et pousser
git add .
git commit -m "Description de la mise à jour"
git push origin main
```

Streamlit Cloud déploiera automatiquement les changements ! 🚀

## 📝 Notes

- L'app prendra ~30 secondes à se charger la première fois
- Streamlit Cloud met en cache les dépendances
- Les performances sont excellentes pour une utilisation interne
- Si tu veux plus de puissance, tu peux passer à Streamlit Cloud PRO

## 🆘 Dépannage

**L'app dit "Resource not found"** → Vérifie que `App_streamlit_eml.py` est à la racine du repo

**Les emails ne s'envoient pas** → Vérifie que les Secrets sont bien configurés dans Streamlit Cloud

**Erreur de certificat** → Assure-toi que `PRIVATE_KEY` est complet dans les Secrets
