from django.core.mail import EmailMessage
from django.conf import settings

def send_statement_email(member, pdf_path, password, period):
    """Send the mini-statement via email."""
    period_map = {
        1: "1 month",
        3: "3 months",
        6: "6 months",
        12: "1 year"
    }
    subject = f"FlexiCash Loan Statement - {period_map.get(period, 'period')}"

    message = (
        f"Dear {member.first_name},<br><br>"
        f"Your mini-statement for the last {period_map.get(period, 'period')} is attached. "
        "Please use the following password to open the document:<br><br>"
        f"<strong>Password: {password}</strong><br><br>"
        "If you have any questions, please contact support.<br><br>"
        "Best regards,<br>FlexiCash Team"
    )

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[member.email],
    )
    email.content_subtype = "html"
    with open(pdf_path, "rb") as pdf_file:
        email.attach('Loan_Statement.pdf', pdf_file.read(), 'application/pdf')
    email.send(fail_silently=False)