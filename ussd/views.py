from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from member.models import FlexiCashMember  # Assuming this is your member model
from .ussd_handlers.registration import handle_registration
from .ussd_handlers.apply_loan import apply_loan_handler
from .ussd_handlers.check_balance import check_balance_handler

@csrf_exempt
def ussd_view(request):
    if request.method == 'POST':
        # Retrieve parameters from POST request
        session_id = request.POST.get("sessionId", "").strip()
        phone_number = request.POST.get("phoneNumber", "").strip()
        text = request.POST.get("text", "").strip()

        # Split the input text to manage navigation
        text_parts = text.split("*")

        # Check if user is registered
        try:
            user = FlexiCashMember.objects.get(phone=phone_number)
            is_registered = True
        except FlexiCashMember.DoesNotExist:
            is_registered = False

        # Routing based on registration status
        if not is_registered:
            # Display welcome message and options to register
            if text == "":
                response = "CON Welcome to FlexiCash Microfinance. Please select an option:\n1. Register"
            else:
                # Pass correct parameters to handle_registration
                response = handle_registration(request, session_id, phone_number, text)  # Correct arguments
        else:
            # Registered user main menu and actions
            if text == "":
                response = "CON Welcome back to FlexiCash.\n1. Apply for Loan\n2. Repay Loan\n3. Check Limit \n4. Request Statement\n5. Exit"
            elif text_parts[0] == "1":  # Apply for Loan
                # Pass the necessary arguments to the apply_loan_handler function
                response = apply_loan_handler(request, session_id, phone_number, text)  # Loan application handler
            elif text_parts[0] == "2":  # Repay Loan
                response = "CON Please enter the amount you want to repay."  # Example placeholder for repayment
            elif text_parts[0] == "3":  # Check Loan Limit
                response = "CON Your loan limit is 50,000."  # Example placeholder for loan limit
            elif text_parts[0] == "4":  # Request Statement
                response = "CON Your loan statement has been sent to your registered email."  # Placeholder for statement
            elif text_parts[0] == "5":  # Exit
                response = "END Thank you for using FlexiCash Microfinance."
            elif text_parts[0] == "0":  # Go Back
                response = "CON Welcome back to FlexiCash.\n1. Apply for Loan\n2. Repay Loan\n3. Check Limit \n4. Request Statement\n5. Exit"
            elif text_parts[0] == "00":  # Main Menu
                response = "CON Welcome back to FlexiCash.\n1. Apply for Loan\n2. Repay Loan\n3. Check Limit \n4. Request Statement\n5. Exit"
            else:
                response = "END Invalid option. Please try again."

        return HttpResponse(response, content_type='text/plain')

    return HttpResponse("Method not allowed", status=405)
