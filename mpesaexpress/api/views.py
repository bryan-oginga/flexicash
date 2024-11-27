from pytz import utc
from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from mpesaexpress.models import MpesaTransaction
import logging

# Configure logging
logger = logging.getLogger(__name__)


class MpesaExpressCallback(APIView):
    def post(self, request, *args, **kwargs):
        try:
            logger.debug("Received M-Pesa Callback: %s", request.data)

            # Extract data from callback
            stk_callback = request.data.get("Body", {}).get("stkCallback", {})
            merchant_request_id = stk_callback.get("MerchantRequestID")
            checkout_request_id = stk_callback.get("CheckoutRequestID")
            result_code = stk_callback.get("ResultCode", -1)
            result_desc = stk_callback.get("ResultDesc", "No description provided")
            items = stk_callback.get("CallbackMetadata", {}).get("Item", [])

            # Extract and initialize transaction data
            amount = next((item["Value"] for item in items if item.get("Name") == "Amount"), None)
            phone_number = next((item["Value"] for item in items if item.get("Name") == "PhoneNumber"), None)
            mpesa_receipt_number = next((item["Value"] for item in items if item.get("Name") == "MpesaReceiptNumber"), None)
            transaction_date = next((item["Value"] for item in items if item.get("Name") == "TransactionDate"), None)

            # Convert transaction date
            try:
                if transaction_date:
                    transaction_datetime = utc.localize(
                        datetime.strptime(str(transaction_date), "%Y%m%d%H%M%S")
                    )
                else:
                    transaction_datetime = None
            except ValueError as ve:
                logger.error("Transaction date parsing error: %s", ve)
                transaction_datetime = None

            # Log parsed data
            logger.info(
                "Parsed Callback Data: MerchantRequestID=%s, CheckoutRequestID=%s, Amount=%s, PhoneNumber=%s, "
                "ReceiptNumber=%s, TransactionDate=%s, ResultCode=%s, ResultDesc=%s",
                merchant_request_id,
                checkout_request_id,
                amount,
                phone_number,
                mpesa_receipt_number,
                transaction_datetime,
                result_code,
                result_desc,
            )

            # Save transaction
            status = "Success" if result_code == 0 else "Failed"
            mpesa_payment = MpesaTransaction.objects.create(
                merchant_request_id=merchant_request_id,
                checkout_request_id=checkout_request_id,
                amount=amount,
                phone_number=phone_number,
                result_code=result_code,
                result_desc=result_desc,
                mpesa_receipt_number=mpesa_receipt_number,
                transaction_date=transaction_datetime,
                status=status,
                callback_url=request.build_absolute_uri(),
            )
            logger.info("M-Pesa Payment Saved: %s", mpesa_payment)

            return Response({"status": "success", "message": "Payment recorded successfully!"}, status=HTTP_200_OK)

        except KeyError as e:
            logger.error("KeyError in M-Pesa callback: %s", e)
            return Response({"error": "Missing required fields", "details": str(e)}, status=HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception("An unexpected error occurred while processing M-Pesa callback")
            return Response({"error": "Unexpected error", "details": str(e)}, status=HTTP_400_BAD_REQUEST)
