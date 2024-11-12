from loanapplication.models import Transaction
from datetime import datetime, timedelta
from django.utils import timezone


def get_transactions(member, period):
    """Retrieves transactions based on the given period in months."""
    start_date = timezone.now() - timedelta(days=period * 30)
    return Transaction.objects.filter(member=member, date__gte=start_date)

def generate_qr_code(member, period):
    # Logic for generating a QR code (e.g., using qrcode library)
    qr_code_path = f"/path/to/qr_codes/qr_{member.id}_{period}.png"
    # Code for creating and saving the QR code
    return qr_code_path