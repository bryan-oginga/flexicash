from django.core.mail import EmailMessage
from django.conf import settings
from pathlib import Path

def send_statement_email(email, pdf_path):
    pdf_file = Path(pdf_path)  # Convert pdf_path to a Path object
    if pdf_file.exists():  # Now we can safely check if it exists
        email_message = EmailMessage(
            subject="Your Mini Statement",
            body="Dear customer, attached is your mini statement.",
            to=[email]
        )
        email_message.attach_file(pdf_path)
        email_message.send()
    else:
        print("PDF file not found.")