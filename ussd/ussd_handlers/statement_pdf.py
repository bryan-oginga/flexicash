from fpdf import FPDF
import qrcode
import os

def create_statement_pdf(member, transactions, period):
    # Set up media directory
    media_dir = os.path.join(os.getcwd(), 'media')
    os.makedirs(media_dir, exist_ok=True)  # Create directory if it doesn't exist
    
    # Set QR code path
    qr_img_path = os.path.join(media_dir, f'qr_{member.id}.png')

    # Generate QR code
    qr = qrcode.make(f'Statement for {member.first_name}, Period: {period}')
    qr.save(qr_img_path)

    # Create the PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Mini Statement for {member.first_name}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Period: {period} months", ln=True, align='C')

    # Add transactions to PDF
    pdf.ln(10)
    pdf.cell(200, 10, txt="Date          Type          Amount", ln=True)
    for transaction in transactions:
        pdf.cell(200, 10, txt=f"{transaction.date}   {transaction.transaction_type}    {transaction.amount}", ln=True)

    # Add QR code to PDF
    pdf.image(qr_img_path, x=10, y=pdf.get_y() + 10, w=30)

    # Save the PDF
    pdf_path = os.path.join(media_dir, f'statement_{member.id}.pdf')
    pdf.output(pdf_path)

    return pdf_path
