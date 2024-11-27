from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from transactions.models import Transaction
import logging
import json
from django.shortcuts import render
import requests
from django.shortcuts import get_object_or_404
from .models import MPesaTransaction
import uuid
from django.conf import settings

PAHERO_API_USERNAME = settings.PAHERO_API_USERNAME
PAHERO_API_PASSWORD = settings.PAHERO_API_PASSWORD
PAHERO_API_ACCOUNT_ID = settings.PAHERO_API_ACCOUNT_ID
PAHERO_API_CHANNEL_ID = settings.PAHERO_API_CHANNEL_ID
PAHERO_API_CALLBACK_URL = settings.PAHERO_API_CALLBACK_URL

# Generate the Basic Auth token
import base64

def generate_basic_auth_token(api_username, api_password):
    credentials = f"{api_username}:{api_password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded_credentials}"

auth_token = generate_basic_auth_token(PAHERO_API_USERNAME, PAHERO_API_PASSWORD)
challenge_token = settings.INTASEND_CHALLENGE_TOKEN

logger = logging.getLogger(__name__)


        
@csrf_exempt
def intasend_stk_webhook(request):
    try:
        # We rerive the webhook resposne
        payload = json.loads(request.body.decode("utf-8"))
        challenge_token = payload.get('challenge')
        invoice_id = payload.get('invoice_id')
        state = payload.get('state')

        # Validate the challenge token
        if challenge_token != settings.INTASEND_CHALLENGE_TOKEN:
            logger.warning("Invalid challenge token received in webhook")
            return JsonResponse({"success": False, "error": "Invalid challenge token"}, status=403)

        # Find the transaction
        transaction = Transaction.objects.filter(invoice_id=invoice_id).first()
        if not transaction:
            logger.warning(f"Transaction with invoice ID {invoice_id} not found")
            return JsonResponse({"success": False, "error": "Transaction not found"}, status=404)

        # Update the transaction state
        if transaction.state != state:
            transaction.state = state
            transaction.save(update_fields=['state'])
            logger.info(f"Transaction {invoice_id} updated to state: {state}")

        return JsonResponse({"success": True, "message": f"Transaction {invoice_id} updated successfully"})

    except json.JSONDecodeError:
        logger.exception("Invalid JSON payload in webhook request")
        return JsonResponse({"success": False, "error": "Invalid JSON payload"}, status=400)

    except Exception as e:
        logger.exception("Error processing webhook")
        return JsonResponse({"success": False, "error": "Internal server error"}, status=500)


def initiate_payhero_stk_push(request):
    # Example input data
    amount = 3
    phone_number = "0799043853"
    channel_id = PAHERO_API_CHANNEL_ID
    external_reference = f"INV-{uuid.uuid4().hex[:6].upper()}"
    callback_url = PAHERO_API_CALLBACK_URL
    
    # Save initial transaction details
    transaction = MPesaTransaction.objects.create(
        external_reference=external_reference,
        amount=amount,
        phone_number=phone_number,
        channel_id=channel_id,
        provider="m-pesa",
    )

    # Generate auth token
    auth_token = generate_basic_auth_token(PAHERO_API_USERNAME, PAHERO_API_PASSWORD)

    # API Headers and Payload
    api_url = "https://backend.payhero.co.ke/api/v2/payments"
    headers = {
        "Authorization": auth_token,
        "Content-Type": "application/json"
    }
    payload = {
        "amount": amount,
        "phone_number": phone_number,
        "channel_id": channel_id,
        "provider": "m-pesa",
        "external_reference": external_reference,
        "callback_url": callback_url
    }

    # Debugging information
    logger.info(f"Auth Token: {auth_token}")
    logger.info(f"Headers: {headers}")
    logger.info(f"Payload: {payload}")

    # Make the API call
    response = requests.post(api_url, json=payload, headers=headers)
    if response.status_code == 201:
        response_data = response.json()
        transaction.status = response_data.get("status")
        transaction.checkout_request_id = response_data.get("CheckoutRequestID")
        transaction.save()
        return JsonResponse({"success": True, "transaction": response_data}, status=201)
    else:
        logger.error(f"API Error: {response.text}")
        return JsonResponse({"success": False, "error": response.json()}, status=response.status_code)


@csrf_exempt
def payhero_callback(request):
    if request.method == "POST":
        data = json.loads(request.body)
        response_data = data.get("response", {})
        
        # Extract details
        external_reference = response_data.get("ExternalReference")
        transaction = get_object_or_404(MPesaTransaction, external_reference=external_reference)
        
        # Update transaction details
        transaction.status = response_data.get("Status")
        transaction.result_code = response_data.get("ResultCode")
        transaction.result_description = response_data.get("ResultDesc")
        transaction.mpesa_receipt_number = response_data.get("MpesaReceiptNumber")
        transaction.save()

        return JsonResponse({"success": True, "message": "Callback received successfully."})
    return JsonResponse({"success": False, "error": "Invalid request method."}, status=400)

