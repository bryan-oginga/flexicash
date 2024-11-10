from decimal import Decimal
from django.shortcuts import get_object_or_404
from ussd import constants
from fleximembers.models import FlexiCashMember
from loanapplication.models import MemberLoanApplication,Transaction
from loanmanagement.models import LoanProduct,FlexiCashLoanApplication

from django.http import HttpResponse


def check_member_exists(phone_number):
    """Checks if the member exists in the database."""
    try:
        return FlexiCashMember.objects.get(phone=phone_number)
    except FlexiCashMember.DoesNotExist:
        return None


def apply_loan_handler(request, session_id, phone_number, text):
    """Handles the loan application process for FlexiCash members."""
    parts = text.split("*")
    member = check_member_exists(phone_number)

    # If member doesn't exist, ask to register
    if not member:
        return HttpResponse("END Member not found. Please register first.", content_type="text/plain")

    # Check if the member has any pending balance (must be zero to apply for a new loan)
    if member.balance > 0:
        return HttpResponse("END You have a pending balance. Please repay before applying for a new loan.", content_type="text/plain")

    # Step 1: Prompt user to select loan type if not already selected
    if len(parts) == 1:
        loan_products = LoanProduct.objects.all()
        loan_options = "\n".join([f"{index+1}. {loan_product.name}" for index, loan_product in enumerate(loan_products)])
        return HttpResponse(f"CON Select Loan Type:\n{loan_options}", content_type="text/plain")

    # Step 2: Capture loan type selection
    elif len(parts) == 2:
        try:
            selected_index = int(parts[1]) - 1
            loan_products = LoanProduct.objects.all()
            loan_product = loan_products[selected_index]
        except (ValueError, IndexError):
            return HttpResponse("END Invalid loan type selected. Please try again.", content_type="text/plain")
        
        # Prompt for loan amount
        return HttpResponse(f"CON Enter loan amount for {loan_product.name}:", content_type="text/plain")

    # Step 3: Enter loan amount
    elif len(parts) == 3:
        try:
            requested_amount = Decimal(parts[2])
        except ValueError:
            return HttpResponse("END Invalid loan amount. Please enter a numeric value.", content_type="text/plain")

        # Check if the requested amount is within the member's loan limit
        if requested_amount > member.loan_limit:
            return HttpResponse("END The requested amount exceeds your loan limit.", content_type="text/plain")
        
        # Prompt for PIN
        return HttpResponse("CON Please enter your PIN to confirm the loan:", content_type="text/plain")

    # Step 4: Enter PIN
    elif len(parts) == 4:
        pin = parts[3]

        # Check if the entered PIN matches the member's stored PIN
        if pin != member.pin:
            return HttpResponse("END Incorrect PIN. Please try again.", content_type="text/plain")
        
        # Get loan type and amount from the previous inputs
        loan_product_index = int(parts[1]) - 1
        loan_products = LoanProduct.objects.all()
        selected_loan_product = loan_products[loan_product_index]
        requested_amount = Decimal(parts[2])

        # Create loan application entry
        MemberLoanApplication.objects.create(
            member=member,
            loan_product=selected_loan_product,
            requested_amount=requested_amount
        )

        # Clear any session or temporary data
        return HttpResponse(f"END Your loan of {requested_amount} for {selected_loan_product.name} has been successfully submitted. We will process your application.", content_type="text/plain")

    return HttpResponse("END Invalid option. Please try again.", content_type="text/plain")
