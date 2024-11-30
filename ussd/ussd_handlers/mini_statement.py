from .statement_logic import get_transactions, generate_statement_rows
from .statement_pdf import create_statement_pdf
from .send_email import send_statement_email
from fleximembers.models import FlexiCashMember
from django.http import HttpResponse

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
        transactions = get_transactions(member, period)
        statement_rows = generate_statement_rows(transactions)
        pdf_path, password = create_statement_pdf(member, statement_rows, period, request)
        send_statement_email(member, pdf_path, password, period)
        return HttpResponse("END Your loan-statement has been sent to your email.")
    else:
        return HttpResponse("END Invalid option.")
