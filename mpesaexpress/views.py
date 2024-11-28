from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from transactions.models import Transaction
from .models import MpesaTransaction
import logging
import json
from django.shortcuts import render
import requests
from django.shortcuts import get_object_or_404
import uuid
import base64
import datetime
logger = logging.getLogger(__name__)
from requests.auth import HTTPBasicAuth


PAHERO_API_USERNAME = settings.PAHERO_API_USERNAME
PAHERO_API_PASSWORD = settings.PAHERO_API_PASSWORD
PAHERO_API_ACCOUNT_ID = settings.PAHERO_API_ACCOUNT_ID
PAHERO_API_CHANNEL_ID = settings.PAHERO_API_CHANNEL_ID
PAHERO_API_CALLBACK_URL = settings.PAHERO_API_CALLBACK_URL
challenge_token = settings.INTASEND_CHALLENGE_TOKEN

PASSKEY = settings.PASSKEY
CONSUMER_KEY = settings.CONSUMER_KEY
CONSUMER_SECRET = settings.CONSUMER_SECRET
ACCESS_TOKEN_URL = settings.ACCESS_TOKEN_URL
MPESA_CALLBACK_URL = settings.MPESA_CALLBACK_URL

# Generate the Basic Auth token

def generate_basic_auth_token(api_username, api_password):
    credentials = f"{api_username}:{api_password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded_credentials}"

auth_token = generate_basic_auth_token(PAHERO_API_USERNAME, PAHERO_API_PASSWORD)
        
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




def generate_password(shortcode, passkey, timestamp):
    password_string = f"{shortcode}{passkey}{timestamp}"
    return base64.b64encode(password_string.encode('utf-8')).decode('utf-8')


def get_access_token():
    consumer_key = CONSUMER_KEY
    consumer_secret = CONSUMER_SECRET
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{consumer_key}:{consumer_secret}'.encode()).decode()}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP codes >= 400
        data = response.json()
        if "access_token" in data:
            return data["access_token"]
        else:
            raise ValueError("Access token not found in response")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching access token: {e}")
        raise
    except ValueError as ve:
        print(f"Unexpected response format: {ve}")
        raise



def initiate_mpesa_stk_push(request):
    try:
        # Mpesa credentials
        shortcode = '174379'
        passkey = PASSKEY
        amount = 2
        phone_number = '254799043853'
        callback_url = MPESA_CALLBACK_URL
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        password = generate_password(shortcode, passkey, timestamp)

        # Payload for the API
        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": str(amount),
            "PartyA": phone_number,
            "PartyB": shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": callback_url,
            "AccountReference": "TestAccount",
            "TransactionDesc": "Payment for service"
        }
        
        access_token = get_access_token()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

        logger.debug("Initiating MPesa STK Push")
        logger.debug(f"URL: {url}")
        logger.debug(f"Headers: {headers}")
        logger.debug(f"Payload: {payload}")

        # Make the API request
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        # Log response details
        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Data: {response.text}")

        if response.status_code == 200:
            response_data = response.json()
            logger.info("Payment request successful.")
            return JsonResponse(response_data)
        else:
            logger.error("Payment request failed.")
            return JsonResponse(
                {"error": "Payment request failed", "details": response.json()},
                status=response.status_code
            )
    except requests.exceptions.RequestException as e:
        logger.exception("A network error occurred.")
        return JsonResponse({"error": "A network error occurred", "details": str(e)}, status=500)
    except Exception as e:
        logger.exception("An unexpected error occurred.")
        return JsonResponse({"error": "An unexpected error occurred", "details": str(e)}, status=500)




