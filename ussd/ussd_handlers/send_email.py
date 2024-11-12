from django.core.mail import EmailMessage
from django.conf import settings
from pathlib import Path
from django.core.mail import send_mail

def send_statement_email(member, pdf_path, password, period):
    # Construct the subject based on the period and member number
    period_map = {
        1: "1 month",
        3: "3 months",
        6: "6 months",
        12: "1 year"
    }
    subject = f"Your {period_map.get(period, 'Statement')} Mini-Statement for Member {member.membership_number}"
    
    # Construct the body with personalized greeting and password information
    message = (
        f"Dear {member.first_name},<br><br>"
        f"Your mini-statement for the last {period_map.get(period, 'period')} is attached. "
        "Please use the following password to open the document:<br><br>"
        f"<strong>Password: {password}</strong><br><br>"
        "If you have any issues, please contact support.<br><br>"
        "Best regards,<br>Flexipay Team"
    )
    
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [member.email]

    # Set the content type of the email to HTML for proper formatting
    email_message = EmailMessage(subject, message, from_email, to_email)
    email_message.content_subtype = "html"  # Set content type to HTML for bold formatting
    
    # Attach the PDF file to the email
    with open(pdf_path, "rb") as pdf_file:
        email_message.attach('statement.pdf', pdf_file.read(), 'application/pdf')
    
    # Send the email
    email_message.send(fail_silently=False)
