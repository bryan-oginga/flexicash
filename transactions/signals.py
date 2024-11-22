import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.db.models import F
from decimal import Decimal
from .models import Transaction
from loanapplication.models import MemberLoanApplication
from fleximembers.models import FlexiCashMember
from django.db.models import Case, When, Value, DecimalField, BooleanField

# Set up logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Transaction)
def handle_loan_balance(sender, instance, created, **kwargs):
    logger.info(f"Transaction Post-Save Signal Triggered for Transaction ID: {instance.invoice_id}")
    
    # Check if transaction is created and the type is 'Repayment'
    if created:
        logger.info(f"New Transaction Created: {instance.invoice_id} - Type: {instance.transaction_type}")
    else:
        logger.info(f"Transaction {instance.invoice_id} updated, but not created.")

    if instance.transaction_type == 'Repayment':
        logger.info(f"Repayment detected for Transaction {instance.invoice_id}")

        # Log the member and loan details
        try:
            member = instance.member
            loan = instance.loan
            amount = Decimal(instance.amount)
            repayment_type = instance.repayment_type

            logger.info(f"Member: {member.phone} - Balance before repayment: {member.member_balance}")
            logger.info(f"Loan ID: {loan.id} - Outstanding Balance before repayment: {loan.outstanding_balance}")
            logger.info(f"Repayment amount: {amount} - Repayment Type: {repayment_type}")

            # Ensure repayment amount is not zero
            if amount <= 0:
                logger.warning(f"Repayment amount is zero or negative for transaction {instance.invoice_id}")
                return

            # Start a transaction block to ensure database consistency
            with transaction.atomic():
                if repayment_type == 'Full':
                    logger.info(f"Handling full repayment for Transaction {instance.invoice_id}")

                    # Update member balance to zero for full repayment
                    member.member_balance = Decimal('0.00')
                    logger.info(f"Member balance updated to: {member.member_balance}")
                    member.save()

                    # Update loan outstanding balance to zero and mark as closed
                    loan.outstanding_balance = Decimal('0.00')
                    loan.payment_complete = True
                    loan.loan_status = 'Closed'
                    logger.info(f"Loan outstanding balance updated to: {loan.outstanding_balance} - Loan Status: {loan.loan_status}")
                    loan.save()

                elif repayment_type == 'Partial':
                    logger.info(f"Handling partial repayment for Transaction {instance.invoice_id}")

                    # Decrease member's balance by the repayment amount
                    member.member_balance = F('member_balance') - amount
                    logger.info(f"Member balance updated to: {member.member_balance}")
                    member.save()

                    # Decrease the loan's outstanding balance
                    loan.outstanding_balance = max(loan.outstanding_balance - amount, Decimal('0.00'))
                    logger.info(f"Loan outstanding balance updated to: {loan.outstanding_balance}")

                    # Check if loan is fully repaid and update status
                    if loan.outstanding_balance == Decimal('0.00'):
                        loan.payment_complete = True
                        loan.loan_status = 'Closed'
                        logger.info(f"Loan marked as completed and closed for transaction {instance.invoice_id}")
                    else:
                        loan.payment_complete = False
                        loan.loan_status = 'Open'
                        logger.info(f"Loan remains open for transaction {instance.invoice_id}")

                    loan.save()

                else:
                    logger.warning(f"Unknown repayment type '{repayment_type}' for transaction {instance.invoice_id}")

                # Refresh member and loan from DB to ensure we have the latest data
                member.refresh_from_db()
                loan.refresh_from_db()

                logger.info(f"Transaction {instance.invoice_id} processed successfully.")
        
        except Exception as e:
            logger.error(f"Error processing repayment for Transaction {instance.invoice_id}: {str(e)}")
            # Optionally, you can raise an error to stop further processing if needed
            raise e

    else:
        logger.info(f"Transaction {instance.invoice_id} is not a repayment, skipping balance update.")
