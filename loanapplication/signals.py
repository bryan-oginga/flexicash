from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from .models import MemberLoanApplication  # Assuming the model is called MemberLoan
from transactions.models import Transaction
from fleximembers.models import FlexiCashMember
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import datetime
import logging
from intasend import APIService
from django.conf import settings

logger = logging.getLogger(__name__)

token = settings.INTASEND_SECRET_KEY
publishable_key   = settings.INTASEND_PUBLISHABLE_KEY
service = APIService(token=token, publishable_key=publishable_key)


@receiver(pre_save, sender=MemberLoanApplication)
def populate_loan_details(sender, instance, **kwargs):
    """
    Auto-populates loan details such as interest rate, total repayment, etc.
    """
    if instance.loan_product:
        loan_product = instance.loan_product
        instance.interest_rate = loan_product.interest_rate
        instance.loan_yield = instance.principal_amount * (instance.interest_rate / Decimal(100))

        # Calculate total repayment
        instance.total_repayment = (
            instance.principal_amount + instance.loan_yield + (instance.loan_penalty or Decimal(0))
        ).quantize(Decimal("0.00"))

        # Calculate penalty only for disbursed loans
        # Calculate penalty only for disbursed loans
    if instance.loan_status == "Approved" and instance.due_date:
        if instance.due_date < timezone.now().date():  # Ensure both are date objects for comparison
            instance.loan_penalty = (instance.total_repayment * Decimal(0.20)).quantize(Decimal("0.00"))
        else:
            instance.loan_penalty = Decimal(0)
      
            
    if instance.loan_status == 'Approved':
            instance.outstanding_balance = instance.total_repayment

    else:
        # Set default values for missing loan_product
        instance.interest_rate = Decimal('0.00')
        instance.loan_yield = Decimal('0.00')
        instance.total_repayment = Decimal('0.00')
        instance.loan_penalty = Decimal('0.00')

def update_member_loan_status(sender, instance, **kwargs):
    """Update the status of MemberLoanApplication based on specific loan actions."""
    
    # Define a mapping only if necessary
    status_mapping = {
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Closed', 'Closed'),
    }

    # Check if the status needs updating
    new_status = status_mapping.get(instance.loan_status)
    if new_status and instance.loan_status != new_status:
        instance.loan_status = new_status
        # Avoid infinite loop by using update instead of save
        MemberLoanApplication.objects.filter(pk=instance.pk).update(loan_status=new_status)
        
        # Log the action
        logger.info(f"Updated loan application {instance.application_ref} to status {new_status}")


#update the Flexicashmember balance to total repayment on disbursement
@receiver(post_save, sender=MemberLoanApplication)
def update_member_balance(sender, instance, created, **kwargs):
    if instance.loan_status == 'Approved':
        try:
            flexicash_member = FlexiCashMember.objects.get(email=instance.member.email)
            flexicash_member.member_balance = instance.total_repayment
            flexicash_member.save()
        except FlexiCashMember.DoesNotExist:
            print("The mmeber does not exist")
        
        
import logging
from intasend import APIService
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MemberLoanApplication

# Configure logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=MemberLoanApplication)
def disburse_loan_on_approval(sender, instance, created, **kwargs):
    """
    Initiates and approves M-Pesa B2C transactions for loan disbursement
    when a loan is approved in the admin panel.
    """
    if instance.loan_status == 'Approved' and instance.disbursement_date is None:
        try:
            # Set up the member and phone number
            member = instance.member
            member_phone = member.phone.lstrip('+')  # Ensure phone number is formatted correctly
            logger.info(f"Member phone number: {member_phone}")

            # Prepare transaction details
            transaction = {
                "name": member.first_name,  # Name of the member
                "account": f"254{member_phone[1:]}",  # Phone number in proper format (2547...)
                "amount": float(instance.principal_amount),  # Loan amount
                "narrative": f"Loan disbursement for {member.membership_number}",  # Purpose of the payment
            }

            # Initialize IntaSend APIService with credentials
            token = "your_intasend_token"  # Replace with your actual token
            private_key = "your_private_key"  # Replace with your private key
            service = APIService(token=token, private_key=private_key)

            # Initiate transfer
            response = service.transfer.mpesa(
                currency="KES",
                transactions=[transaction],
                requires_approval="YES",  # Ensure approval is required
            )

            # Log the response
            logger.info(f"IntaSend Initiate Response: {response}")

            # Handle approval if needed
            if response.get("requires_approval", "NO") == "YES":
                approval_response = service.transfer.approve(response)
                logger.info(f"IntaSend Approval Response: {approval_response}")

                # Confirm success and update disbursement date
                if approval_response.get("status") == "SUCCESS":
                    instance.disbursement_date = timezone.now()
                    instance.save(update_fields=["disbursement_date"])
                    logger.info(f"Loan disbursed successfully for {member.first_name} ({member.membership_number})")
                else:
                    logger.error(f"Approval failed for {member.first_name} ({member.membership_number}): {approval_response}")
            else:
                # Direct disbursement without approval (if applicable)
                instance.disbursement_date = timezone.now()
                instance.save(update_fields=["disbursement_date"])
                logger.info(f"Loan disbursed without approval for {member.first_name} ({member.membership_number})")

        except Exception as e:
            logger.error(f"Error during loan disbursement for {instance.member.first_name}: {str(e)}", exc_info=True)
