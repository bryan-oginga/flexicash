from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import LoanMpesaTransaction
from intasend import APIService
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

token = settings.INSTASEND_SECRET_KEY
publishable_key = settings.INSTASEND_PUBLISHABLE_KEY
service = APIService(token=token, publishable_key=publishable_key, test=True)

@shared_task
def check_payment_status(invoice_id, response):
    logger.info(f"Checking payment status for invoice {invoice_id}. Response received: {response}")
    
    try:
        # Retrieve the transaction object from the database using the invoice_id
        transaction = LoanMpesaTransaction.objects.get(invoice_id=invoice_id)

        # Extract the payment state from the response
        state = response.get('invoice', {}).get('state', '')
        
        if state == 'PENDING':
            # If the state is pending, mark the transaction as pending or leave it as is
            transaction.state = 'PENDING'
            transaction.save()
            logger.info(f"Transaction {invoice_id} is still pending.")
        elif state == 'SUCCESS':
            # If the state is successful, mark the transaction as completed
            transaction.state = 'COMPLETED'
            transaction.save()
            logger.info(f"Transaction {invoice_id} marked as completed.")
        else:
            # If the state is something else (like failed or unknown), mark it as failed
            transaction.state = 'FAILED'
            transaction.save()
            logger.info(f"Transaction {invoice_id} marked as failed.")
    
    except Exception as e:
        logger.error(f"Error checking payment status for invoice {invoice_id}: {str(e)}")
