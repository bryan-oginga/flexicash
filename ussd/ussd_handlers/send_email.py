from django.core.mail import EmailMessage
from django.conf import settings
from pathlib import Path
from django.core.mail import EmailMessage

from django.core.mail import EmailMessage

def send_statement_email(member_email, pdf_path):
    subject = "Your Mini Statement from Flexipay"
    message = "Please find your mini statement attached. The PDF is password-protected."

    email = EmailMessage(subject, message, 'noreply@flexipay.com', [member_email])
    email.attach_file(pdf_path)
    email.send()
