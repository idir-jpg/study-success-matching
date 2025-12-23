import os
import tempfile
import pandas as pd
from email.message import EmailMessage
import mimetypes

def generate_mandat_email(selected_row, mandat_pdf_path):
    email = selected_row.get('Mail')
    if not email or pd.isna(email):
        raise ValueError("Adresse e-mail invalide ou manquante pour l'élève.")

    msg = EmailMessage()
    msg['To'] = email
    msg['Subject'] = "📄 Signature du mandat - Study Success"
    msg.set_content("""Bonjour,

J'espère que vous allez bien.  
Pour commencer les cours de manière légale, nous avons besoin que vous remplissiez et signiez le mandat ci-joint.

Comme expliqué, il ne vous engage à rien après cette première heure de cours.

Bien à vous,  
L'équipe Study Success
""")

    # Joindre le PDF avec nom personnalisé
    if os.path.isfile(mandat_pdf_path):
        with open(mandat_pdf_path, 'rb') as f:
            file_data = f.read()
            mime_type, _ = mimetypes.guess_type(mandat_pdf_path)
            maintype, subtype = mime_type.split('/') if mime_type else ('application', 'pdf')
            msg.add_attachment(
                file_data,
                maintype=maintype,
                subtype=subtype,
                filename="Mandat Study Success_ Particulier Employeur.pdf"
            )
    else:
        raise FileNotFoundError(f"Fichier non trouvé : {mandat_pdf_path}")

    # Enregistrement du fichier .emltpl
    with tempfile.NamedTemporaryFile(delete=False, suffix=".emltpl", mode='wb') as f:
        f.write(bytes(msg))
        return f.name
