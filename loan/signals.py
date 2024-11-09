import random
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from loan.models import LoanApplication
from member.models import MemberLoan,FlexiCashMember
from .models import LoanApplication
from member.models import MemberLoan  # Import the related model
from django.utils import timezone
from decimal import Decimal


def generate_unique_loan_id():
    """
    Generates a unique loan ID with the prefix FCL-00 followed by a random number.
    Ensures that the generated ID is unique in the LoanApplication model.
    """
    while True:
        # Generate a random number (you can adjust the range as needed)
        random_number = random.randint(1000, 9999)
        loan_id = f"FCL-00{random_number}"

        # Check if the loan ID already exists in the LoanApplication model
        if not LoanApplication.objects.filter(loan_id=loan_id).exists():
            return loan_id  # Return the unique loan ID if it doesn't exist


@receiver(post_save, sender=MemberLoan)
def create_loan_application(sender, instance, created, **kwargs):
    if created:
        loan_id = generate_unique_loan_id()

        # Create a LoanApplication instance
        loan_application = LoanApplication.objects.create(
            member=instance.member,
            loan_type=instance.loan_type,
            amount_requested=instance.requested_amount,
            interest_rate=instance.interest_rate,
            interest_amount=instance.interest_amount,
            total_repayment=instance.total_repayment,
            loan_profit=instance.total_repayment - instance.requested_amount,
            loan_status=instance.status,
            loan_due_date=instance.due_date,
            loan_balance=instance.total_repayment,
            loan_duration=instance.loan_type.loan_duration,
            loan_id=loan_id
        )
        
        print(f"Loan Application {loan_application.loan_id} created for Member {instance.member.membership_number}.")


@receiver(post_save, sender=LoanApplication)
def update_member_loan_status(sender, instance, **kwargs):
    # Get the related MemberLoan instance
    try:
        member_loan = MemberLoan.objects.get(member=instance.member, loan_type=instance.loan_type)
    except MemberLoan.DoesNotExist:
        return  # Handle missing MemberLoan instance if needed

    # Synchronize MemberLoan status based on LoanApplication status
    if instance.loan_status == 'Approved':
        member_loan.status = 'Approved'
    elif instance.loan_status == 'Dirsbured':
        member_loan.status = 'Rejected'
    elif instance.loan_status == 'Rejected':
        member_loan.status = 'Rejected'
    elif instance.loan_status == 'Repaid':
        member_loan.status = 'Repaid'
    elif instance.loan_status == 'Defaulted':
        member_loan.status = 'Defaulted'
    else:
        member_loan.status = 'Pending'  # Default or fallback status

    member_loan.save()
    
    
@receiver(post_save, sender=LoanApplication)
def update_member_balance_on_disbursement(sender, instance, **kwargs):
    # Check if the loan status is 'DISBURSED'
    if instance.loan_status == 'Disbursed' and instance.disbursed == True:
        # Try to retrieve the MemberLoan instance that matches the LoanApplication
        try:
            member_loan = MemberLoan.objects.get(member=instance.member, loan_type=instance.loan_type)
            member = member_loan.member  # Retrieve the associated FlexiCashMember from MemberLoan
        except MemberLoan.DoesNotExist:
            # If the MemberLoan does not exist, we could log an error or handle it as needed
            print("No MemberLoan associated with this LoanApplication.")
            return

        # Update the member's balance by adding the disbursed loan amount
        member.balance += Decimal(instance.amount_requested)
        
        # Save the updated balance to the database
        member.save()