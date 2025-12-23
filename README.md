# 🧑‍🏫 Study Success - Interface Matching Elève / Professeur

Une application Streamlit pour automatiser l'envoi d'emails de coordination entre élèves et professeurs via Office 365.

## 🎯 Fonctionnalités

- **Recherche élève** : Trouvez rapidement un élève par prénom/nom
- **Sélection professeur** : Filtrez les professeurs disponibles en temps réel
- **Aperçu du mail** : Visualisez l'email avant envoi
- **Envoi automatique** : Envoyez les coordonnées via Microsoft Graph API
- **Mode test** : Testez sans risque (tous les mails vont à idir.hadjhamou@study-success.fr)
- **Envoi du mandat** : Envoyer les mandats signés aux parents

## 🚀 Installation locale

### Prérequis
- Python 3.9+
- Accès à SharePoint Study Success
- Certificat Microsoft Graph configuré

### Étapes

1. **Cloner le repository**
```bash
git clone https://github.com/YourUsername/study-success-matching.git
cd study-success-matching
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configurer les variables d'environnement**
Créer un fichier `.env` à la racine :
```
TENANT_ID=51065c1e-192f-467c-be56-f9225e88ebae
CLIENT_ID=5ea4abfc-d7f5-41e2-ab5f-f34ef0af8c37
CERT_THUMBPRINT=4C1D8CB0300C79139133D72DE4D3336F613ECB5E
CERT_PRIVATE_KEY_PATH=mailer.key
GOOGLE_API_KEY=votre_cle_google
```

4. **Lancer l'application**
```bash
streamlit run App_streamlit_eml.py
```

L'app sera accessible à `http://localhost:8501`

## 🌐 Accès en ligne

L'application est déployée sur Streamlit Cloud :
**[https://study-success-matching.streamlit.app](https://study-success-matching.streamlit.app)**

## 📧 Configuration des senders

Les senders configurés :
- idir.hadjhamou@study-success.fr → Idir HADJ HAMOU
- manon.curie@study-success.fr → Manon CURIE
- lucas.ledanois@study-success.fr → Lucas LE DANOIS
- mathilde.boher@study-success.fr → Agathe BOHER

## 📂 Structure du projet

```
├── App_streamlit_eml.py       # Application principale
├── email_prof_eml.py          # Génération d'emails
├── send_mail_streamlit.py     # Envoi via Microsoft Graph
├── Graph_Api.py               # Téléchargement SharePoint
├── mandat.py                  # Génération mandats
├── requirements.txt           # Dépendances Python
├── .env                       # Variables d'environnement (non committé)
├── .gitignore                 # Fichiers à ignorer
└── README.md                  # Ce fichier
```

## 🔐 Sécurité

- Le fichier `.env` n'est **jamais** commité sur GitHub
- Sur Streamlit Cloud, les secrets sont gérés via le dashboard
- Les certificats sont stockés en local et non partagés

## 👥 Utilisation par l'équipe

1. Un member de l'équipe ouvre le lien Streamlit Cloud
2. Sélectionne un élève
3. Sélectionne un professeur
4. Envoie les coordonnées
5. Le mail est envoyé automatiquement !

## 🤝 Contribution

Pour toute modification :
1. Créer une branche : `git checkout -b feature/ma-feature`
2. Committer les changements : `git commit -m "Description"`
3. Pousser : `git push origin feature/ma-feature`
4. Créer une Pull Request

## 📞 Support

Pour toute question, contacter Idir HADJ HAMOU

## 📄 Licence

© 2025 Study Success - Tous droits réservés
