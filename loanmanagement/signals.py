# loanmanagement/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from loanmanagement.models import FlexiCashLoanApplication
from loanapplication.models import MemberLoanApplication
from fleximembers.models  import FlexiCashMember

@receiver(post_save, sender=FlexiCashLoanApplication)
def update_member_loan_status(sender, instance, **kwargs):
    """Update the status of MemberLoanApplication based on FlexiCashLoanApplication actions."""

    # Find the corresponding MemberLoanApplication
    try:
        member_loan_application = MemberLoanApplication.objects.get(
            member=instance.member, 
            loan_product=instance.loan_product, 
            principal_amount=instance.principal_amount,
            payment_complete = False,
            
            
        )
    except MemberLoanApplication.DoesNotExist:
        return  # Exit if no matching MemberLoanApplication is found

    # Map FlexiCashLoanApplication status to MemberLoanApplication status
    status_mapping = {
        'Approved': 'Approved',
        'Rejected': 'Rejected',
        'Disbursed': 'Disbursed',
        'Closed': 'Completed',  # Assuming 'Completed' is the equivalent status in MemberLoanApplication
    }

    # Set the MemberLoanApplication status based on the manager's action
    new_status = status_mapping.get(instance.loan_status)
    if new_status:
        member_loan_application.loan_status = new_status
        member_loan_application.save()

        # Optionally log for debugging
        print(f"Updated MemberLoanApplication {member_loan_application.pk} to status {new_status}")


#update memebers balance on disbursement
@receiver(post_save, sender=FlexiCashLoanApplication)
def update_member_balance_on_disbursement(sender, instance, **kwargs):
    # Check if the loan status is "Disbursed" and approval date is set
    if instance.loan_status == "Disbursed":
        # Get the related member
        member = instance.member

        # Update the member's balance with the loan's total repayment amount
        member.member_balance += instance.total_repayment
        member.save()
        
        
        
       