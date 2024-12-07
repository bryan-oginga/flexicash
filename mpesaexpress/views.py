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


