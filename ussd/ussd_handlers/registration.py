from django.http import HttpResponse
from member.models import FlexiCashMember  # Import your member model
from django.db import IntegrityError

def check_member_exists(phone_number):
    """Checks if the member already exists in the database."""
    try:
        return FlexiCashMember.objects.get(phone=phone_number)
    except FlexiCashMember.DoesNotExist:
        return None
def normalize_phone(phone):
    """Normalize phone numbers to +2547... format."""
    if not phone:
        return "Phone number is missing."  # or you could raise an error or return None

    if phone.startswith('07'):
        return '+254' + phone[1:]
    elif phone.startswith('254'):
        return '+' + phone
    elif phone.startswith('+254'):
        return phone
    
    return "Invalid phone format. Please start with 07, 254, or +254."

def handle_registration(request, session_id, phone_number, text):
    """Handles the registration process for FlexiCash members."""
    parts = text.split('*')
    normalized_phone = normalize_phone(phone_number)
    
    # If phone format is invalid, return an error response
    if normalized_phone == "Invalid phone format. Please start with 07, 254, or +254.":
        response = "END " + normalized_phone
        return HttpResponse(response, content_type="text/plain")
    
    # Check if the member already exists
    member = check_member_exists(normalized_phone)
    
    # Handle the registration flow based on the text parts
    if parts == ['']:
        # Show options if session is empty
        if member:
            response = "CON Choose an option:\n1. Apply Loan\n2. Pay Loan\n3. Check Loan Limit\n4. Mini Statement\n"
        else:
            response = "CON Welcome to FlexiCash Microfinance\n1. Register\n"
    elif parts == ['1'] and not member:
        response = "CON Please enter your First Name:"
    elif len(parts) == 2 and not member:
        first_name = parts[1]
        response = "CON Please enter your Last Name:"
    elif len(parts) == 3 and not member:
        last_name = parts[2]
        response = "CON Please enter email:"
    elif len(parts) == 4 and not member:
        # Collect email and ask for PIN
        email = parts[3]
        response = "CON Please enter a 4-digit PIN:"
    elif len(parts) == 5 and not member:
        # Collect PIN and ask for confirmation
        pin = parts[4]
        response = "CON Please confirm your PIN:"
    elif len(parts) == 6 and not member:
        confirmed_pin = parts[5]
        first_name = parts[1]
        last_name = parts[2]
        email = parts[3]
        pin = parts[4]
        
        if pin != confirmed_pin:
            # Check if PINs match
            response = "END The PINs do not match. Please start again."
        else:
            # Proceed with registration
            if FlexiCashMember.objects.filter(email=email).exists():
                response = "END This email is already registered. Try a different email."
            elif FlexiCashMember.objects.filter(phone=normalized_phone).exists():
                response = "END This phone number is already registered. Try a different phone number."
            else:
                try:
                    # Create and save the new member
                    member = FlexiCashMember(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        phone=normalized_phone,
                        pin=pin,
                        balance=0.00  # Explicitly setting the balance
                    )
                    member.save()
                    response = "END Registration successful! You can now use FlexiCash services."
                except IntegrityError:
                    response = "END Registration error. Please try again."

    else:
        response = "END Invalid choice. Please try again."

    return HttpResponse(response, content_type="text/plain")