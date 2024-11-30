from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from django.conf import settings
import os
import PyPDF2
from .statement_logic import generate_statement_rows  # Import here

def create_statement_pdf(member, transactions, period, request):
    """
    Create and protect a mini-statement PDF for the member.
    """
    # Generate the statement rows from the transactions
    statement_rows = generate_statement_rows(transactions)

    # Render the HTML for the statement
    html_content = render_to_string('mini_statement.html', {
        'member': member,
        'transactions': statement_rows,
        'period': period,
        'date': transactions[0].date.strftime('%Y-%m-%d') if transactions else "",
        'total_paid': sum(row['amount'] for row in statement_rows if row['description'] == 'Repayment'),
        'current_balance': sum(row['amount'] for row in statement_rows if row['description'] == 'Disbursement') - 
                           sum(row['amount'] for row in statement_rows if row['description'] == 'Repayment'),
    })

    # Set CSS for the PDF
    css = CSS(string=''' 
        @page { size: A4 portrait; margin: 10mm; }
        body { font-size: 12px; font-family: Arial, sans-serif; }
    ''')

    # Define file path for the generated PDF
    pdf_output_path = os.path.join(settings.MEDIA_ROOT, f'statement_{member.id}.pdf')

    # Generate PDF from the HTML
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(pdf_output_path, stylesheets=[css])

    # Generate password for PDF protection
    password = f"{member.membership_number}{member.first_name[0]}{member.last_name[0]}".upper()

    # Encrypt the PDF with the generated password
    protected_pdf_output_path = pdf_output_path.replace(".pdf", "_protected.pdf")
    with open(pdf_output_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        writer = PyPDF2.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.encrypt(password)

        # Save the protected PDF
        with open(protected_pdf_output_path, "wb") as protected_pdf_file:
            writer.write(protected_pdf_file)

    return protected_pdf_output_path, password
