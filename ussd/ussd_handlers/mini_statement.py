from django.http import HttpResponse
from .statement_logic import get_transactions
from .statement_pdf import create_statement_pdf
from .send_email import send_statement_email
from fleximembers.models import FlexiCashMember




def mini_statement_handler(request, session_id, phone_number, text):
    text_parts = text.split("*")

    if len(text_parts) == 1:
        return HttpResponse("CON Choose statement period:\n1. 1 month\n2. 3 months\n3. 6 months\n4. 12 months")

    try:
        member = FlexiCashMember.objects.get(phone=phone_number)
    except FlexiCashMember.DoesNotExist:
        return HttpResponse("END Member not found. Please register first.")

    period_options = {"1": 1, "2": 3, "3": 6, "4": 12}
    period = period_options.get(text_parts[1])

    if period:
        # Get the transactions for the given period
        transactions = get_transactions(member, period)

        # Generate the PDF and get the file path
        pdf_path, password = create_statement_pdf(member, transactions, period, request)

        # Send the email with the mini-statement attached and the password
        send_statement_email(member, pdf_path, password, period)

        return HttpResponse("END Your mini-statement has been sent to your email.")
    else:
        return HttpResponse("END Invalid option.")
