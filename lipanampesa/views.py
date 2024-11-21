from intasend import APIService
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings
from .models import LoanMpesaTransaction
# from .validators import validate_params
# from .utils import initiatite_stk_push
import logging
import json

logger = logging.getLogger(__name__)

# IntaSend configuration
token = settings.INTASEND_SECRET_KEY
publishable_key   = settings.INTASEND_PUBLISHABLE_KEY
service = APIService(token=token, publishable_key=publishable_key , test=True)
challenge_token = settings.INTASEND_CHALLENGE_TOKEN
intasend_webhook_url = settings.INTASEND_WEBHOOK_URL 


@csrf_exempt
def mpesa_payment(request):
    return render(request, 'payment.html', {})


    
@require_POST
@csrf_exempt
def initiate_stk_push_view(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        amount = request.POST.get('amount')
        narrative = request.POST.get('narrative')
        email = request.POST.get('email')

        try:
            # Initiate the STK push with IntaSend
            response = service.collect.mpesa_stk_push(
                phone_number=phone_number,
                amount=amount,
                narrative=narrative,
                email=email,
            )

            # Extract relevant data from the response
            invoice_data = response.get("invoice", {})
            invoice_id = invoice_data.get("invoice_id")
            state = invoice_data.get("state", "PENDING")

            # Save the transaction to the database
            transaction = LoanMpesaTransaction.objects.create(
                invoice_id=invoice_id,
                phone_number=phone_number,
                email=email,
                amount=amount,
                narrative=narrative,
                state=state,  # Default state is 'PENDING'
            )

            logger.info(f"Transaction saved with Invoice ID: {invoice_id}")

            return JsonResponse({
                "success": True,
                "message": "STK push initiated successfully.",
                "transaction": {
                    "invoice_id": transaction.invoice_id,
                    "state": transaction.state,
                    "amount": transaction.amount,
                    "phone_number": transaction.phone_number,
                }
            })

        except Exception as e:
            logger.exception("Error during payment initiation")
            return JsonResponse({"success": False, "error": "An internal server error occurred."}, status=500)

        

@csrf_exempt
def intasend_webhook(request):
    """
    Handle webhook events from IntaSend to update payment status.
    """
    try:
        # Parse JSON payload
        payload = json.loads(request.body.decode("utf-8"))
        challenge_token = payload.get('challenge')
        invoice_id = payload.get('invoice_id')
        state = payload.get('state')

        # Validate the challenge token
        if challenge_token != settings.INTASEND_CHALLENGE_TOKEN:
            logger.warning("Invalid challenge token received in webhook")
            return JsonResponse({"success": False, "error": "Invalid challenge token"}, status=403)

        # Find the transaction in the database
        try:
            transaction = LoanMpesaTransaction.objects.get(invoice_id=invoice_id)
        except LoanMpesaTransaction.DoesNotExist:
            logger.warning(f"Transaction with invoice ID {invoice_id} not found")
            return JsonResponse({"success": False, "error": "Transaction not found"}, status=404)

        # Update the transaction state
        transaction.state = state
        transaction.save()

        logger.info(f"Transaction {invoice_id} updated to state: {state}")

        # Return success response
        return JsonResponse({"success": True, "message": f"Transaction {invoice_id} updated successfully"})

    except json.JSONDecodeError:
        logger.exception("Invalid JSON payload in webhook request")
        return JsonResponse({"success": False, "error": "Invalid JSON payload"}, status=400)

    except Exception as e:
        logger.exception("Error processing webhook")
        return JsonResponse({"success": False, "error": "Internal server error"}, status=500)
