from django.template.loader import render_to_string
from weasyprint import HTML
import os
import PyPDF2
from django.conf import settings
import qrcode

def create_statement_pdf(member, transactions, period):
    # Generate the HTML content using Django's template rendering system
    html_content = render_to_string('mini_statement_template.html', {
        'member': member,
        'transactions': transactions,
        'period': period,
        'date': transactions[0].date.strftime('%Y-%m-%d'),  # Using the first transaction's date
        'qr_image_path': generate_qr_code(member, period)  # Generate QR code path
    })

    # Generate PDF from the HTML content
    pdf_output_path = os.path.join(settings.MEDIA_ROOT, f'statement_{member.id}.pdf')
    HTML(string=html_content).write_pdf(pdf_output_path)

    # Add password protection using PyPDF2
    password = "securepassword"  # Set your desired password here
    with open(pdf_output_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        writer = PyPDF2.PdfWriter()
        
        # Add all pages from the reader to the writer
        for page_num in range(len(reader.pages)):
            writer.add_page(reader.pages[page_num])
        
        # Add password
        writer.encrypt(password)
        
        # Save the new PDF with password protection
        protected_pdf_output_path = pdf_output_path.replace(".pdf", "_protected.pdf")
        with open(protected_pdf_output_path, "wb") as protected_pdf_file:
            writer.write(protected_pdf_file)

    # Return the path to the protected PDF
    return protected_pdf_output_path

def generate_qr_code(member, period):
    # Generate the QR code data
    qr_data = f"Member: {member.first_name} {member.last_name}, Period: {period} months"
    qr_img = qrcode.make(qr_data)

    # Save the QR code image temporarily
    qr_img_path = os.path.join(settings.MEDIA_ROOT, f'qr_{member.id}.png')
    qr_img.save(qr_img_path)

    return qr_img_path
