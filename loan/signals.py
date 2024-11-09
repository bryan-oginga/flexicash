import random
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from loan.models import LoanApplication
from member.models import MemberLoan


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
    """
    Create a LoanApplication record when a new MemberLoan is created.
    The LoanApplication will be associated with the MemberLoan and FlexiCashMember.
    """
    if created:
        # Generate a unique loan ID
        loan_id = generate_unique_loan_id()

        # Create a LoanApplication instance
        loan_application = LoanApplication.objects.create(
            member=instance.member,
            loan_type=instance.loan_type,
            amount_requested=instance.amount,
            interest_rate=instance.interest_rate,
            interest_amount=instance.interest_amount,
            total_repayment=instance.total_repayment,
            profit=instance.total_repayment - instance.amount,
            application_status='PENDING',
            loan_due_date=instance.due_date,
            loan_duration=instance.loan_type.loan_duration,
            loan_id=loan_id,  # Assign the generated loan ID
        )
        
        # Optionally log the application creation or notify the admin
        print(f"Loan Application {loan_application.loan_id} created for Member {instance.member.membership_number}.")
