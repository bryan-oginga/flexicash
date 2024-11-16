from transactions.models import Transaction
from datetime import timedelta
from django.utils import timezone
import qrcode
import os
from django.conf import settings

def get_transactions(member, period):
    """Retrieve transactions based on the given period in months."""
    start_date = timezone.now() - timedelta(days=period * 30)
    return Transaction.objects.filter(member=member, date__gte=start_date)

def calculate_balance(transactions):
    """Calculate the loan balance based on disbursements and repayments."""
    balance = 0
    for transaction in transactions:
        if transaction.transaction_type == 'Disbursement':
            balance += transaction.amount
        elif transaction.transaction_type == 'Repayment':
            balance -= transaction.amount
    return balance

def generate_qr_code(member, period):
    # Retrieve the most recent active loan for the member, if any
    active_loan = member.loans.filter(loan_status__in=["Disbursed", "Approved"]).first()
    
    # If there’s no active loan, handle accordingly
    if not active_loan:
        raise ValueError("No active loan found for this member.")

    # Create QR code content with member details and loan information
    qr_content = (
        f"Member: {member.first_name} {member.last_name}, "
        f"Loan ID: {active_loan.application_id}, "
        f"Period: {period} months"
    )

    # Set the directory path and filename
    qr_directory = os.path.join(settings.MEDIA_ROOT, "qr_codes")
    os.makedirs(qr_directory, exist_ok=True)  # Create directory if it doesn't exist

    # File path for the QR code image
    qr_code_path = os.path.join(qr_directory, f"qr_{member.id}_{period}.png")

    # Generate and save the QR code image
    qr_code = qrcode.make(qr_content)
    qr_code.save(qr_code_path)

    return qr_code_path
