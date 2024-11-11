from fpdf import FPDF
import qrcode
import os
import PyPDF2
from django.conf import settings

def create_statement_pdf(member, transactions, period):
    # Create PDF object
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Set Title
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 0, 255)  # Blue text color
    pdf.cell(200, 10, txt=f"Mini Statement for {member.first_name} {member.last_name}", ln=True, align='C')

    # Add a Line Break
    pdf.ln(10)

    # Add Date and Period
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)  # Black text
    pdf.cell(200, 10, txt=f"Statement Period: {period} months", ln=True)
    pdf.cell(200, 10, txt=f"Date: {transactions[0].date.strftime('%Y-%m-%d')}", ln=True)

    # Add a Line Break
    pdf.ln(10)

    # Create Table for Transaction History
    pdf.set_font("Arial", size=12)
    pdf.cell(40, 10, 'Date', border=1)
    pdf.cell(60, 10, 'Transaction Type', border=1)
    pdf.cell(40, 10, 'Amount', border=1, align='R')
    pdf.ln()

    # Add Table Content
    for transaction in transactions:
        pdf.cell(40, 10, transaction.date.strftime('%Y-%m-%d'), border=1)
        pdf.cell(60, 10, transaction.transaction_type, border=1)
        pdf.cell(40, 10, f'{transaction.amount}', border=1, align='R')
        pdf.ln()

    # Add a Line Break
    pdf.ln(10)

    # Add Footer with Custom Message
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, txt="Thank you for using Flexipay! For support, contact us at support@flexipay.com", ln=True, align='C')

    # Generate QR Code
    qr_data = f"Member: {member.first_name} {member.last_name}, Period: {period} months"
    qr_img = qrcode.make(qr_data)

    # Save the QR code image temporarily
    qr_img_path = os.path.join(settings.MEDIA_ROOT, f'qr_{member.id}.png')
    qr_img.save(qr_img_path)

    # Add the QR code image to the PDF
    pdf.ln(10)
    pdf.image(qr_img_path, x=160, w=30)

    # Output the PDF to a file
    pdf_output_path = os.path.join(settings.MEDIA_ROOT, f'statement_{member.id}.pdf')
    pdf.output(pdf_output_path)

    # Delete the temporary QR code image file
    os.remove(qr_img_path)

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
