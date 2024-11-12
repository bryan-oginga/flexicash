from weasyprint import HTML, CSS
import PyPDF2
import os
from django.template.loader import render_to_string
from django.conf import settings
from .statement_logic import generate_qr_code  # Assuming QR code generation is in statement_logic

def create_statement_pdf(member, transactions, period, request):
    # Calculate total amount paid and final loan balance
    total_paid = sum(transaction.amount for transaction in transactions if transaction.transaction_type == 'Repayment')

    # Generate the QR code for authenticity
    qr_image_path = generate_qr_code(member, period)

    # Generate the HTML content
    html_content = render_to_string('mini_statement.html', {
        'member': member,
        'transactions': transactions,
        'period': period,
        'date': transactions[0].date.strftime('%Y-%m-%d') if transactions else "",
        'qr_image_path': qr_image_path,
        'loan_id': transactions[0].loan.id if transactions else "",
        'loan_type': transactions[0].loan.loan_product.name if transactions else "",  # Corrected line
        'member_id': member.membership_number,
        'total_paid': total_paid,
    })

    # Define A4 page size, reduced margins, and table styling
    css = CSS(string=''' 
        @page {
            size: A4 portrait;
            margin: 3mm 5mm; /* Narrow margins */
        }
        body {
            font-size: 10px;
            font-family: Arial, sans-serif;
        }
        .header, .footer {
            text-align: center;
            font-weight: bold;
        }
        .qr-code {
            width: 100px;
            height: 100px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        table, th, td {
            border: 1px solid #ddd;
            padding: 4px;
            text-align: center;
        }
        .summary {
            text-align: right;
            font-weight: bold;
        }
    ''')

    # Define the PDF output path
    pdf_output_path = os.path.join(settings.MEDIA_ROOT, f'statement_{member.id}.pdf')

    # Generate the PDF with specified CSS
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(pdf_output_path, stylesheets=[css])

    # Generate a password based on member ID and initials
    password = f"{member.membership_number}{member.first_name[0]}{member.last_name[0]}".upper()

    # Add password protection using PyPDF2
    with open(pdf_output_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        writer = PyPDF2.PdfWriter()

        for page_num in range(len(reader.pages)):
            writer.add_page(reader.pages[page_num])

        writer.encrypt(password)

        protected_pdf_output_path = pdf_output_path.replace(".pdf", "_protected.pdf")
        with open(protected_pdf_output_path, "wb") as protected_pdf_file:
            writer.write(protected_pdf_file)

    return protected_pdf_output_path, password
