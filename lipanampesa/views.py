from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from transactions.models import Transaction
from .models import MpesaPayment
import logging
import json
from django.shortcuts import render
import requests
from django.shortcuts import get_object_or_404
import uuid
import base64
import datetime
logger = logging.getLogger(__name__)


PAHERO_API_USERNAME = settings.PAHERO_API_USERNAME
PAHERO_API_PASSWORD = settings.PAHERO_API_PASSWORD
PAHERO_API_ACCOUNT_ID = settings.PAHERO_API_ACCOUNT_ID
PAHERO_API_CHANNEL_ID = settings.PAHERO_API_CHANNEL_ID
PAHERO_API_CALLBACK_URL = settings.PAHERO_API_CALLBACK_URL
challenge_token = settings.INTASEND_CHALLENGE_TOKEN

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



def generate_password(shortcode, passkey, timestamp):
    password_string = f"{shortcode}{passkey}{timestamp}"
    return base64.b64encode(password_string.encode('utf-8')).decode('utf-8')

def get_access_token():
    consumer_key = "WumSttSJpeqk2HONJJtTg0w1oRaPVwQZF22HpRI8VAbVZx5K"
    consumer_secret = "MEtFVM2mp9O2WKAT8GBI3IKA6Vn88AJ7nytMgTblsw9RJtT1WwGcllftp0uGjehH"

    auth_string = f"{consumer_key}:{consumer_secret}"
    auth_base64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    headers = {
        "Authorization": f"Basic {auth_base64}"
    }
    response = requests.get(url, headers=headers)
    response_data = response.json()
    return response_data.get('access_token')

access_token = get_access_token()
print("Access Token:", access_token)

def initiate_mpesa_stk_push(request):
    shortcode = '174379' 
    passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  
    amount = 5  
    phone_number = '254799043853' 
    callback_url = 'https://flexicash-23ff5ac55c24.herokuapp.com/payment/mpesa_callback/' 
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    password = generate_password(shortcode, passkey, timestamp)

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
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()
        return JsonResponse(response_data) 
    else:
        return JsonResponse({"error": "Payment request failed", "details": response.json()})




@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":
        callback_data = request.body
        data = json.loads(callback_data)

        # Extracting values from the response
        result_code = data.get("Body", {}).get("stkCallback", {}).get("ResultCode")
        result_desc = data.get("Body", {}).get("stkCallback", {}).get("ResultDesc")
        mpesa_receipt_number = data.get("Body", {}).get("stkCallback", {}).get("CallbackMetadata", {}).get("Item", [{}])[1].get("Value")
        phone_number = data.get("Body", {}).get("stkCallback", {}).get("CallbackMetadata", {}).get("Item", [{}])[3].get("Value")
        amount = data.get("Body", {}).get("stkCallback", {}).get("CallbackMetadata", {}).get("Item", [{}])[0].get("Value")

        # Create the MpesaPayment record
        try:
            mpesa_payment = MpesaPayment(
                merchant_request_id=data.get("Body", {}).get("stkCallback", {}).get("MerchantRequestID"),
                checkout_request_id=data.get("Body", {}).get("stkCallback", {}).get("CheckoutRequestID"),
                amount=amount,
                phone_number=phone_number,
                transaction_desc="Payment for service",  # Adjust if needed
                result_code=result_code,
                result_desc=result_desc,
                mpesa_receipt_number=mpesa_receipt_number,
                transaction_date=datetime.datetime.now(),  # Timestamp from callback can be used
                callback_url=request.build_absolute_uri(),
                status="Completed" if result_code == 0 else "Failed"
            )
            mpesa_payment.save()  # Save the payment record
            print("Transaction saved:", mpesa_payment)  # Log for debugging

        except Exception as e:
            print("Error saving transaction:", e)  # Log any errors during save

        # Return appropriate response based on result_code
        if result_code == 0:
            return JsonResponse({"message": "Payment successful", "receipt_number": mpesa_receipt_number})
        else:
            return JsonResponse({"message": "Payment failed", "error": result_desc})

    return JsonResponse({"error": "Invalid request method"})
