import logging
import time
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F
from django.db import transaction
from .models import Transaction
from loanapplication.models import MemberLoanApplication
from fleximembers.models import FlexiCashMember

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from decimal import Decimal
from .models import Transaction
from loanapplication.models import MemberLoanApplication
from fleximembers.models import FlexiCashMember

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Transaction)
def handle_transaction_state_change(sender, instance, created, **kwargs):
    if created:
        logger.info(f"New Transaction Created: {instance.invoice_id} with state {instance.state}")
    else:
        logger.info(f"Transaction {instance.invoice_id} updated to state: {instance.state}")

    # Trigger processing only when state changes to COMPLETE
    if instance.state == 'COMPLETE':
        logger.info(f"Transaction {instance.invoice_id} is now COMPLETE. Triggering repayment logic.")
        process_transaction(instance)


def process_transaction(instance):
    """Handles the actual repayment logic."""
    logger.info(f"Processing repayment for Transaction {instance.invoice_id}")

    try:
        # Retrieve related data
        member = instance.member
        loan = instance.loan
        amount = Decimal(instance.amount)
        repayment_type = instance.repayment_type

        logger.debug(f"Member: {member.first_name} - Balance: {member.member_balance}")
        logger.debug(f"Loan ID: {loan.id} - Outstanding Balance: {loan.outstanding_balance}")
        logger.debug(f"Repayment Amount: {amount} - Repayment Type: {repayment_type}")

        # Validate data
        if not member or not loan:
            logger.error(f"Transaction {instance.invoice_id} is invalid: Missing associated Member or Loan.")
            return

        if amount <= 0:
            logger.error(f"Transaction {instance.invoice_id} has invalid amount: {amount}. Skipping.")
            return

        if loan.outstanding_balance <= Decimal('0.00'):
            logger.warning(f"Loan {loan.id} already fully repaid. No updates needed.")
            return

        # Update balances in an atomic transaction
        with transaction.atomic():
            if repayment_type == 'Full':
                logger.info(f"Processing full repayment for Transaction {instance.invoice_id}.")
                FlexiCashMember.objects.filter(id=member.id).update(member_balance=Decimal('0.00'))
                MemberLoanApplication.objects.filter(id=loan.id).update(
                    outstanding_balance=Decimal('0.00'),
                    payment_complete=True,
                    loan_status='Closed'
                )
            elif repayment_type == 'Partial':
                logger.info(f"Processing partial repayment for Transaction {instance.invoice_id}.")
                FlexiCashMember.objects.filter(id=member.id).update(member_balance=F('member_balance') - amount)
                MemberLoanApplication.objects.filter(id=loan.id).update(outstanding_balance=F('outstanding_balance') - amount)

                # Refresh loan to check if fully repaid
                loan.refresh_from_db()
                if loan.outstanding_balance <= Decimal('0.00'):
                    loan.payment_complete = True
                    loan.loan_status = 'Closed'
                else:
                    loan.payment_complete = False
                    loan.loan_status = 'Open'
                loan.save()
            else:
                logger.error(f"Unknown repayment type '{repayment_type}' for Transaction {instance.invoice_id}. Skipping.")

        logger.info(f"Transaction {instance.invoice_id} processed successfully.")

    except Exception as e:
        logger.exception(f"Error processing Transaction {instance.invoice_id}: {e}")
