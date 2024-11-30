from .statement_logic import generate_statement_rows
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
import os
import PyPDF2
from django.conf import settings

def create_statement_pdf(member, transactions, period, request):
    # Retrieve an active loan
    active_loan = member.loans.filter(loan_status__in=["Approved", "Active"]).first()
    if not active_loan:
        raise ValueError("No active loan found for the member.")

    # Generate rows for the statement
    statement_rows = generate_statement_rows(transactions)

    # Generate HTML content for the PDF
    html_content = render_to_string('mini_statement.html', {
        'member': member,
        'transactions': statement_rows,
        'period': period,
        'date': transactions[0].date.strftime('%Y-%m-%d') if transactions else "",
        'loan_id': active_loan.application_ref,
        'loan_type': active_loan.loan_product.name,
        'member_id': member.membership_number,
        'total_paid': sum(row['amount'] for row in statement_rows if row['description'] != 'Disbursement'),
        'current_balance': statement_rows[-1]['balance'] if statement_rows else 0,
    })

    # Define CSS for PDF styling
    css = CSS(string=''' 
        @page { size: A4 portrait; margin: 1mm 3mm; }
        body { font-size: 10px; font-family: Arial, sans-serif; }
    ''')

    # Output paths and password protection setup
    pdf_output_path = os.path.join(settings.MEDIA_ROOT, f'statement_{member.id}.pdf')
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(pdf_output_path, stylesheets=[css])

    # Password generation
    password = f"{member.membership_number}{member.first_name[0]}{member.last_name[0]}".upper()

    # Encrypt PDF
    with open(pdf_output_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        writer = PyPDF2.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.encrypt(password)

        protected_pdf_output_path = pdf_output_path.replace(".pdf", "_protected.pdf")
        with open(protected_pdf_output_path, "wb") as protected_pdf_file:
            writer.write(protected_pdf_file)

    return protected_pdf_output_path, password
