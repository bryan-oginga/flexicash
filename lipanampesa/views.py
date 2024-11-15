# from django.http import JsonResponse
# from django.conf import settings
# from .models import LoanMpesaTransaction
# from intasend import APIService
# import logging
# from django.views.decorators.csrf import csrf_exempt
# from django.shortcuts import render
# from django.views.decorators.csrf import csrf_exempt
# from .tasks import check_payment_status  # Import Celery task for status checking
# from datetime import timezone
# logger = logging.getLogger(__name__)

# # Initialize IntaSend APIService
# token = settings.INSTASEND_SECRET_KEY
# publishable_key = settings.INSTASEND_PUBLISHABLE_KEY
# service = APIService(token=token, publishable_key=publishable_key, test=True)

# @csrf_exempt
# def mpesa_payment(request):
#     context = {
#     }
#     return render(request, 'payment.html', context)

# from django.http import JsonResponse
# from django.conf import settings
# from .models import LoanMpesaTransaction
# from intasend import APIService
# import logging
# from django.utils import timezone
# from django.views.decorators.csrf import csrf_exempt

# logger = logging.getLogger(__name__)

# # Initialize IntaSend APIService with sandbox/test mode enabled
# service = APIService(token=settings.INSTASEND_SECRET_KEY, 
#                      publishable_key=settings.INSTASEND_PUBLISHABLE_KEY, 
#                      test=True)

# def initiate_stk_push(request):
#     if request.method == 'POST':
#         phone_number = '254799043853'
#         amount = 1
#         narrative = 'Purchase'

#         try:
#             # Send payment request to IntaSend
#             response = service.collect.mpesa_stk_push(
#                 phone_number=phone_number,
#                 amount=amount,
#                 narrative=narrative
#             )

#             # Get the invoice_id for status checking
#             invoice_id = response['invoice']['invoice_id']
#             logger.info(f"STK Push initiated, invoice_id: {invoice_id}")

#             # Return a success response with invoice_id for status tracking
#             return JsonResponse({
#                 "success": True,
#                 "message": "Payment initiation successful. Awaiting confirmation.",
#                 "invoice_id": invoice_id
#             })

#         except Exception as e:
#             logger.error(f"Unexpected error during payment initiation: {str(e)}")
#             return JsonResponse({
#                 "success": False,
#                 "error": "An error occurred while initiating payment."
#             }, status=500)

#     return JsonResponse({"error": "Only POST requests are allowed."}, status=400)