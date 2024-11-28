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
        ('Active', 'Active'),
    }

    # Check if the status needs updating
    new_status = status_mapping.get(instance.loan_status)
    if new_status and instance.loan_status != new_status:
        instance.loan_status = new_status
        # Avoid infinite loop by using update instead of save
        MemberLoanApplication.objects.filter(pk=instance.pk).update(loan_status=new_status)
        
        # Log the action
        logger.info(f"Updated loan application {instance.application_ref} to status {new_status}")


@receiver(post_save, sender=MemberLoanApplication)
def update_member_balance(sender, instance, created, **kwargs):
    if instance.loan_status == 'Approved':
        try:
            flexicash_member = FlexiCashMember.objects.get(email=instance.member.email)
            flexicash_member.member_balance = instance.total_repayment
            flexicash_member.save()
        except FlexiCashMember.DoesNotExist:
            print("The mmeber does not exist")
        
        
