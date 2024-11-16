# from django.http import JsonResponse
# from intasend import APIService
# import logging
# from django.conf import settings

# # Initialize IntaSend APIService with sandbox/test mode enabled
# service = APIService(token=settings.INSTASEND_SECRET_KEY, 
#                      publishable_key=settings.INSTASEND_PUBLISHABLE_KEY, 
#                      test=True)

# logger = logging.getLogger(__name__)

# def initiate_stk_push(phone_number, amount, narrative="Full Repayment"):
#     try:
#         # Send payment request to IntaSend
#         response = service.collect.mpesa_stk_push(
#             phone_number=phone_number,
#             amount=amount,
#             narrative=narrative
#         )
#         # Get the invoice_id for status checking
#         invoice_id = response['invoice']['invoice_id']
#         logger.info(f"STK Push initiated, invoice_id: {invoice_id}")

#         # Return a dictionary instead of JsonResponse for better handling
#         return {
#             "success": True,
#             "message": "Payment initiation successful. Awaiting confirmation.",
#             "invoice_id": invoice_id
#         }

#     except Exception as e:
#         logger.error(f"Unexpected error during payment initiation: {str(e)}")
#         return {
#             "success": False,
#             "error": "An error occurred while initiating payment."
#         }
