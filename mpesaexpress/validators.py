from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def validate_params(phone_number, amount, email):
    # Validate phone number (simple check for digits and length)
    if not phone_number.isdigit() or len(phone_number) < 10:
        raise ValueError("Invalid phone number")

    # Validate amount (positive number)
    if float(amount) <= 0:
        raise ValueError("Amount must be greater than 0")

    # Validate email format
    try:
        validate_email(email)
    except ValidationError:
        raise ValueError("Invalid email address")
