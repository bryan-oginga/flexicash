from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import TinyPesaTransaction
from intasend import APIService
import logging
from django.conf import settings


token = settings.INSTASEND_SECRET_KEY
publishable_key = settings.INSTASEND_PUBLISHABLE_KEY
service = APIService(token=token, publishable_key=publishable_key, test=True)


logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5)
def check_payment_status(self, invoice_id):
    """
    Check the payment status for a given invoice ID and update the database.
    """
    try:
        # Fetch the status from IntaSend
        response = service.collect.status(invoice_id=invoice_id)
        status = response.get('invoice', {}).get('state')
        
        # Log the response for debugging
        logger.info(f"Payment status for {invoice_id}: {status}")
        
        # Update the database record
        transaction = TinyPesaTransaction.objects.filter(narrative=invoice_id).first()
        if transaction:
            transaction.state = status
            transaction.updated_at = response['invoice']['updated_at']
            transaction.save()

            if status == "COMPLETE":
                logger.info(f"Transaction {invoice_id} marked as COMPLETE.")
                return {"success": True, "message": "Payment completed successfully."}

            elif status == "FAILED":
                logger.error(f"Transaction {invoice_id} marked as FAILED.")
                return {"success": False, "message": "Payment failed."}

        else:
            logger.error(f"No transaction found for invoice_id: {invoice_id}")

    except Exception as e:
        logger.exception(f"Error checking payment status for {invoice_id}")
        raise self.retry(exc=e, countdown=60)  # Retry after 1 minute
