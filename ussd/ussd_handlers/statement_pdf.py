# statement_pdf.py
from .statement_logic import generate_qr_code, calculate_balance
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
import os
import PyPDF2
from django.conf import settings

def create_statement_pdf(member, transactions, period, request):
    # Retrieve an active loan to include in the statement
    active_loan = member.loans.filter(loan_status__in=["Approved","Active"]).first()
    if not active_loan:
        raise ValueError("No active loan found for the member.")

    # Calculate the loan balance based on transactions
    current_balance = calculate_balance(transactions)

    # Generate QR code for the statement
    qr_image_path = generate_qr_code(member, period)

    # Generate HTML content for the PDF
    html_content = render_to_string('mini_statement.html', {
        'member': member,
        'transactions': transactions,
        'period': period,
        'date': transactions[0].date.strftime('%Y-%m-%d') if transactions else "",
        'qr_image_path': qr_image_path,  # Path to QR code image
        'loan_id': active_loan.application_ref,
        'loan_type': active_loan.loan_product.name,
        'member_id': member.membership_number,
        'total_paid': sum(t.amount for t in transactions if t.transaction_type == 'Repayment'),
        'current_balance': current_balance,  # Display current balance in PDF
    })

    # Define CSS for PDF styling
    # Define CSS for PDF styling
    css = CSS(string=''' 
        @page { size: A4 portrait; margin: 1mm 3mm; }
        body { font-size: 10px; font-family: Arial, sans-serif; }
        .qr-code { width: 100px; height: 100px; }
    ''')

    # Output paths and password protection setup
    pdf_output_path = os.path.join(settings.MEDIA_ROOT, f'statement_{member.id}.pdf')
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(pdf_output_path, stylesheets=[css])

    # Password generation (using member's details)
    password = f"{member.membership_number}{member.first_name[0]}{member.last_name[0]}".upper()

    # Encrypt PDF for protection
    with open(pdf_output_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        writer = PyPDF2.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.encrypt(password)
        
        # Save the protected PDF
        protected_pdf_output_path = pdf_output_path.replace(".pdf", "_protected.pdf")
        with open(protected_pdf_output_path, "wb") as protected_pdf_file:
            writer.write(protected_pdf_file)

    return protected_pdf_output_path, password