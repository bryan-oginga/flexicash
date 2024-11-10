import random
from django.db.models.signals import post_save
from django.dispatch import receiver
from loan.models import LoanApplication
from member.models import MemberLoan, FlexiCashMember
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


def generate_unique_loan_id():
    """
    Generates a unique loan ID with the prefix FCL-00 followed by a random number.
    Ensures that the generated ID is unique in the LoanApplication model.
    """
    while True:
        random_number = random.randint(1000, 9999)
        loan_id = f"FCL-00{random_number}"
        if not LoanApplication.objects.filter(loan_id=loan_id).exists():
            return loan_id
def create_loan_application(sender, instance, created, **kwargs):
    if created:
        loan_id = generate_unique_loan_id()

        # Ensure the requested_amount and interest_rate are not None
        if instance.requested_amount is None or instance.interest_rate is None:
            logger.error(f"Loan amount or interest rate is None for MemberLoan {instance.id}")
            return

        # Perform calculations only if values are valid
        interest_amount = instance.requested_amount * instance.interest_rate / Decimal(100)
        total_repayment = instance.requested_amount + interest_amount
        loan_profit = total_repayment - instance.requested_amount

        loan_application = LoanApplication.objects.create(
            member=instance.member,
            loan_type=instance.loan_type,
            amount_requested=instance.requested_amount,
            interest_rate=instance.interest_rate,
            interest_amount=interest_amount,
            total_repayment=total_repayment,
            loan_profit=loan_profit,
            loan_status=instance.status,
            loan_due_date=instance.due_date,
            loan_balance=total_repayment,
            loan_duration=instance.loan_type.loan_duration,
            loan_id=loan_id
        )

        logger.info(f"Loan Application {loan_application.loan_id} created for Member {instance.member.membership_number}.")

@receiver(post_save, sender=LoanApplication)
def update_member_balance_on_disbursement(sender, instance, **kwargs):
    if instance.loan_status == 'Disbursed':
        try:
            member_loan = MemberLoan.objects.filter(
                member=instance.member, loan_type=instance.loan_type
            ).order_by('-created_at').first()

            if member_loan:
                member = member_loan.member
                member.balance += Decimal(instance.amount_requested)  # Update balance
                member.save()
                logger.info(f"Updated balance for {member.membership_number}: {member.balance}")
            else:
                logger.error(f"No MemberLoan found for Member {instance.member.membership_number}")
        except Exception as e:
            logger.error(f"Error updating balance for Member {instance.member.membership_number}: {e}")


@receiver(post_save, sender=LoanApplication)
def update_member_loan_status(sender, instance, **kwargs):
    try:
        member_loan = MemberLoan.objects.get(member=instance.member, loan_type=instance.loan_type)
        member_loan.status = instance.loan_status
        member_loan.save()
        logger.info(f"Updated MemberLoan status for {instance.member.membership_number} to {instance.loan_status}")
    except MemberLoan.DoesNotExist:
        logger.error(f"No matching MemberLoan found for LoanApplication {instance.loan_id}")
