from intasend import APIService
from .validators import validate_params
import logging
from django.conf import settings
from .models import MPesaTransaction
import requests
import json
import base64

logger = logging.getLogger(__name__)

tinypesa_username = settings.TINYPESA_API_KEY
tinypesa_api_key = settings.TINYPESA_USERNAME
tinypesa_base_url = settings.TINYPESA_BASE_URL

payhero_username = settings.PAYHERO_USERNAME
payhero_password = settings.PAYHERO_PASSWORD
payhero_endpoint_url = settings.PAYHERO_ENDPOINT_URL
payhero_callback_url = settings.PAYHERO_CALLBACK_URL
payhero_channel_id = settings.PAYHERO_CHANNEL_ID

credentials = f'{payhero_username}:{payhero_password}'
encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
basic_auth_token = f'Basic {encoded_credentials}'
print(basic_auth_token)

def initiate_stk_push(phone_number, amount, account_no):
    url = payhero_endpoint_url
    headers = {
        'Content-Type': 'application/json',
        'Authorization': basic_auth_token
    }

    try:
        amount = float(amount)  # Ensure it's a float
    except ValueError:
        raise ValueError(f"Invalid amount: {amount} cannot be converted to float.")

    # Create and save the transaction before making the API request
    transaction = MPesaTransaction.objects.create(
        external_reference=account_no,
        amount=amount,
        phone_number=phone_number,
        channel_id=payhero_channel_id,
        payment_status="QUEUED",
        status="PENDING"
    )

    # Now, initiate the STK push
    data = {
        "amount": amount,
        "phone_number": phone_number,
        "channel_id": payhero_channel_id, 
        "provider": "m-pesa", 
        "external_reference": account_no,
        "callback_url": payhero_callback_url
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        # Optionally update the transaction after successful initiation (e.g., set the checkout request ID)
        transaction.checkout_request_id = response.json().get('CheckoutRequestID')
        transaction.save()
        print("Payment initiated successfully.")
        return response.json()  # Return response if needed
    else:
        transaction.status = "FAILED"
        transaction.save()
        print("Failed to initiate payment.")
        return None

   



















# def initiate_stk_push(phone_number, amount, account_no):
#     url = tinypesa_base_url

#     headers = {
#         'Accept': 'application/json',
#         'Apikey': tinypesa_api_key,
#         'Content-Type': 'application/json',
#     }

#     data = {
#         'username': tinypesa_username,
#         'msisdn': phone_number,
#         'amount': amount,
#         'account_no': account_no,
#     }

#     try:
#         response = requests.post(url, headers=headers, data=json.dumps(data))

#         if response.status_code == 200:
#             try:
#                 return response.json()
#             except requests.exceptions.JSONDecodeError:
#                 logger.error("Failed to decode JSON response from TinyPesa")
#                 return None
#         else:
#             logger.error(f"Request failed with status {response.status_code}: {response.text}")
#             return None

#     except requests.exceptions.RequestException as e:
#         logger.error(f"An error occurred while making the request: {e}")
#         return None



# def process_stk_push(phone_number, amount, narrative, email):
#     """
#     Initiate STK Push via IntaSend.
#     """
#     try:
#         # Send STK Push request
#         response = service.collect.mpesa_stk_push(
#             phone_number=phone_number,
#             amount=amount,
#             narrative=narrative,
#             email=email,
#         )

#         # Save initial transaction details
#         invoice_id = response['invoice']['invoice_id']
#         state = response['invoice']['state']
#         trans_id = response['id']
#         created_at = response['invoice']['created_at']
#         updated_at = response['invoice']['updated_at']

#         LoanMpesaTransaction.objects.create(
#             phone_number=phone_number,
#             amount=amount,
#             narrative=invoice_id,
#             trans_id=trans_id,
#             state=state,
#             created_at=created_at,
#             updated_at=updated_at,
#         )

#         logger.info(f"STK Push initiated successfully, invoice_id: {invoice_id}")
#         return {"success": True, "message": "Payment initiation successful. Awaiting confirmation."}

#     except Exception as e:
#         logger.exception("Error initiating STK Push")
#         return {"success": False, "message": "Payment initiation failed."}

# def handle_webhook_payload(payload):
#     """
#     Handle webhook payload to update payment status.
#     """
#     try:
#         invoice = payload.get('invoice', {})
#         invoice_id = invoice.get('invoice_id')
#         state = invoice.get('state')
#         trans_id = payload.get('id')

#         # Find and update the transaction in the database
#         transaction = LoanMpesaTransaction.objects.filter(narrative=invoice_id).first()

#         if transaction:
#             transaction.state = state
#             transaction.trans_id = trans_id
#             transaction.updated_at = invoice.get('updated_at')
#             transaction.save()
#             logger.info(f"Transaction {invoice_id} updated to state: {state}")
#             return {"success": True, "message": "Transaction updated successfully."}
#         else:
#             logger.warning(f"Transaction with Invoice ID {invoice_id} not found.")
#             return {"success": False, "error": "Transaction not found."}
#     except Exception as e:
#         logger.exception("Error processing webhook payload")
#         return {"success": False, "error": "Internal server error."}
