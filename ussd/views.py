from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from fleximembers.models import FlexiCashMember
from ussd.ussd_handlers.registration import handle_registration
from ussd.ussd_handlers.apply_loan import apply_loan_handler
from ussd.ussd_handlers.repay_loan import repay_loan_handler
from ussd.ussd_handlers.check_limit import check_limit_handler
from ussd.ussd_handlers.mini_statement import mini_statement_handler
from ussd import constants

@csrf_exempt
def ussd_view(request):
    if request.method != 'POST':
        return HttpResponse("Method not allowed", status=405)

    session_id = request.POST.get("sessionId", "").strip()
    phone_number = request.POST.get("phoneNumber", "").strip()
    text = request.POST.get("text", "").strip()
    text_parts = text.split("*")

    response = ""  # Default response variable

    try:
        user = FlexiCashMember.objects.get(phone=phone_number)
        is_registered = True
    except FlexiCashMember.DoesNotExist:
        is_registered = False

    if not is_registered:
        # Registration Process
        if text == "":
            response = constants.WELCOME_MESSAGE_NEW_USER
        else:
            response = handle_registration(request, session_id, phone_number, text)
    else:
        # Main Menu for Registered Users
        if text == "":
            response = constants.WELCOME_MESSAGE_REGISTERED_USER
        elif text_parts[0] == "1":
            response = apply_loan_handler(request, session_id, phone_number, text)
        elif text_parts[0] == "2":
            # User selects "Repay Loan"
            response = repay_loan_handler(request, session_id, phone_number, text)
        elif text_parts[0] == "3":
            response = check_limit_handler(request, session_id, phone_number, text)
        elif text_parts[0] == "4":
            # User selects "Request Mini Statement"
            response = mini_statement_handler(request, session_id, phone_number, text)
        elif text_parts[0] == "5":
            response = constants.EXIT_MESSAGE
        else:
            response = constants.INVALID_OPTION

    return HttpResponse(response, content_type='text/plain')
