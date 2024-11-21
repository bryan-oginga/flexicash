from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render
# from .utils import process_stk_push
import logging
from django.conf import settings
# from .utils import process_stk_push, handle_webhook_payloa
from .models import MPesaTransaction
from .utils import initiate_stk_push
import uuid
import json

logger = logging.getLogger(__name__)



def mpesa_payment(request):
    return render(request, 'payment.html')


@csrf_exempt
def stk_push_view(request):
    if request.method == "POST":
        phone_number = request.POST.get("phone_number")
        amount = request.POST.get("amount")
        account_no = request.POST.get("account_no")

        response = initiate_stk_push(phone_number, amount, account_no)
        if response and response.get("CheckoutRequestID"):
            # Optionally, save the transaction details here if necessary
            return JsonResponse({"success": True, "message": "Payment initiated successfully."})
        else:
            return JsonResponse({"success": False, "message": "Failed to initiate payment."})

    return JsonResponse({"success": False, "message": "Invalid request method."})

@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
            logger.info("Received callback payload: %s", payload)

            # Extract necessary information from the callback payload
            checkout_request_id = payload.get("response", {}).get("CheckoutRequestID")
            mpesa_receipt_number = payload.get("response", {}).get("MpesaReceiptNumber")
            result_code = payload.get("response", {}).get("ResultCode")
            result_desc = payload.get("response", {}).get("ResultDesc")
            external_reference = payload.get("response", {}).get("ExternalReference")

            # Update the transaction status based on the callback
            transaction = MPesaTransaction.objects.filter(external_reference=external_reference).first()

            if transaction:
                transaction.result_code = result_code
                transaction.result_desc = result_desc
                transaction.mpesa_receipt_number = mpesa_receipt_number
                transaction.status = "SUCCESS" if result_code == 0 else "FAILED"
                transaction.save()

                return JsonResponse({"success": True, "message": "Transaction updated successfully."})
            else:
                return JsonResponse({"success": False, "message": "Transaction not found."})

        except Exception as e:
            logger.error("Error processing callback: %s", e)
            return JsonResponse({"success": False, "message": "Error processing callback."})
    
    return JsonResponse({"success": False, "message": "Invalid request method."})




# @csrf_exempt
# def tinypesa_webhook(request):
#     if request.method == "POST":
#         payload = json.loads(request.body)
#         stk_callback = payload.get("Body", {}).get("stkCallback", {})

#         result_code = stk_callback.get("ResultCode")
#         external_reference = stk_callback.get("ExternalReference")
#         mpesa_receipt = None
#         transaction_date = None

#         # Check if the transaction was successful
#         if result_code == 0:
#             metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
#             for item in metadata:
#                 if item["Name"] == "MpesaReceiptNumber":
#                     mpesa_receipt = item["Value"]
#                 if item["Name"] == "TransactionDate":
#                     transaction_date = item["Value"]

#         # Update the transaction in the database
#         try:
#             transaction = TinyPesaTransaction.objects.get(account_no=external_reference)
#             transaction.is_complete = result_code == 0
#             transaction.result_code = result_code
#             transaction.result_description = stk_callback.get("ResultDesc")
#             transaction.mpesa_receipt = mpesa_receipt
#             transaction.transaction_date = transaction_date
#             transaction.save()

#             return JsonResponse({"success": True, "message": "Transaction updated successfully."})
#         except TinyPesaTransaction.DoesNotExist:
#             return JsonResponse({"success": False, "message": "Transaction not found."})

#     return JsonResponse({"success": False, "message": "Invalid request method."})


# @require_POST
# @csrf_exempt
# def initiate_stk_push_view(request):
#     if request.method == 'POST':
#         phone_number = request.POST.get('phone_number')
#         amount = request.POST.get('amount')
#         narrative = request.POST.get('narrative')
#         email = request.POST.get('email')

#         try:
#             response = process_stk_push(
#                 phone_number=phone_number,
#                 amount=amount,
#                 narrative=narrative,
#                 email=email,
#             )
#             return JsonResponse(response)
#         except Exception as e:
#             logger.exception("Error during payment initiation")
#             return JsonResponse({"success": False, "error": "An internal server error occurred."}, status=500)

# @require_POST
# @csrf_exempt
# def intasend_webhook(request):
#     """
#     Handle webhook events from IntaSend to update payment status.
#     """
#     try:
#         payload = request.json()
#         challenge_token = payload.get('challenge')

#         # Validate the challenge token
#         if challenge_token != settings.INTASEND_CHALLENGE_TOKEN:
#             logger.warning("Invalid challenge token")
#             return JsonResponse({"success": False, "error": "Invalid challenge token"}, status=403)

#         # Process the webhook payload
#         response = handle_webhook_payload(payload)
#         return JsonResponse(response)

#     except Exception as e:
#         logger.exception("Error processing webhook")
#         return JsonResponse({"success": False, "error": "Internal server error."}, status=500)
