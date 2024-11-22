import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.db.models import F
from decimal import Decimal
from .models import Transaction
from loanapplication.models import MemberLoanApplication
from fleximembers.models import FlexiCashMember

# Set up logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Transaction)
def handle_loan_balance(sender, instance, created, **kwargs):
    logger.info(f"Transaction Post-Save Signal Triggered for Transaction ID: {instance.invoice_id}")
    
    # Check if transaction is newly created and of type 'Repayment'
    if not created or instance.transaction_type != 'Repayment':
        logger.info(f"Transaction {instance.invoice_id} is not a new repayment, skipping balance update.")
        return

    logger.info(f"Processing repayment for Transaction {instance.invoice_id}")

    try:
        # Retrieve necessary details
        member = instance.member
        loan = instance.loan
        amount = Decimal(instance.amount)
        repayment_type = instance.repayment_type

        logger.info(f"Member: {member.first_name} - Initial Balance: {member.member_balance}")
        logger.info(f"Loan ID: {loan.id} - Initial Outstanding Balance: {loan.outstanding_balance}")
        logger.info(f"Repayment Amount: {amount} - Repayment Type: {repayment_type}")

        # Ensure repayment amount is valid
        if amount <= 0:
            logger.warning(f"Repayment amount is zero or negative for Transaction {instance.invoice_id}. Skipping.")
            return

        # Start an atomic transaction for consistency
        with transaction.atomic():
            if repayment_type == 'Full':
                logger.info(f"Handling full repayment for Transaction {instance.invoice_id}")

                # Update balances for full repayment
                FlexiCashMember.objects.filter(id=member.id).update(member_balance=Decimal('0.00'))
                MemberLoanApplication.objects.filter(id=loan.id).update(
                    outstanding_balance=Decimal('0.00'),
                    payment_complete=True,
                    loan_status='Closed'
                )
                logger.info(f"Full repayment processed: Member and loan balances set to zero.")

            elif repayment_type == 'Partial':
                logger.info(f"Handling partial repayment for Transaction {instance.invoice_id}")

                # Deduct repayment amount from member balance and loan outstanding balance
                FlexiCashMember.objects.filter(id=member.id).update(member_balance=F('member_balance') - amount)
                MemberLoanApplication.objects.filter(id=loan.id).update(outstanding_balance=F('outstanding_balance') - amount)

                # Refresh objects from the database to get updated values
                member.refresh_from_db()
                loan.refresh_from_db()

                logger.info(f"Updated Member Balance: {member.member_balance}")
                logger.info(f"Updated Loan Outstanding Balance: {loan.outstanding_balance}")

                # Check if loan is fully repaid
                if loan.outstanding_balance <= Decimal('0.00'):
                    loan.payment_complete = True
                    loan.loan_status = 'Closed'
                    logger.info(f"Loan fully repaid and closed.")
                else:
                    loan.payment_complete = False
                    loan.loan_status = 'Open'
                    logger.info(f"Loan remains open.")

                # Save loan status changes
                loan.save()
            else:
                logger.warning(f"Unknown repayment type '{repayment_type}' for Transaction {instance.invoice_id}. Skipping.")

        logger.info(f"Transaction {instance.invoice_id} processed successfully.")
    
    except Exception as e:
        logger.error(f"Error processing repayment for Transaction {instance.invoice_id}: {str(e)}")
        raise e
