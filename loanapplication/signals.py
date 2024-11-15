from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from .models import MemberLoanApplication,Transaction  # Assuming the model is called MemberLoan
from loanmanagement.models import LoanProduct,FlexiCashLoanApplication
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

@receiver(pre_save, sender=MemberLoanApplication)
def populate_loan_details(sender, instance, **kwargs):
    """
    This function auto-populates the loan fields such as loan_product,
    interest_rate, total_repayment, etc., when a loan application is saved.
    """
    if instance.loan_product:
        loan_product = instance.loan_product  # Get the selected loan product
        
        # Auto-populate interest rate from the selected loan product
        instance.interest_rate = loan_product.interest_rate
        
        # Calculate interest and total repayment
        instance.loan_yield = instance.principal_amount * (instance.interest_rate / Decimal(100))
        instance.total_repayment = (instance.principal_amount + instance.loan_yield).quantize(Decimal("0.01"))
        
        # Set the due date based on the loan duration
        instance.due_date = timezone.now().date() + timezone.timedelta(days=loan_product.loan_duration)

        # Optionally, you can also populate other fields based on your business logic
        # For example, set the loan balance to the requested amount when the loan is first applied
        instance.loan_balance = instance.principal_amount

    else:
        # If for some reason there's no loan product, set default values or raise an error
        instance.loan_product = None
        instance.interest_rate = Decimal('0.00')
        instance.total_repayment = Decimal('0.00')
        instance.due_date = None
        instance.loan_balance = Decimal('0.00')
        
        



@receiver(post_save, sender=MemberLoanApplication)
def create_flexicash_loan_application(sender, instance, created, **kwargs):
    """Create a corresponding FlexiCashLoanApplication whenever a MemberLoanApplication is saved."""
    if created:
        # Extract data from the MemberLoanApplication instance
        member = instance.member
        loan_product = instance.loan_product
        principal_amount = instance.principal_amount
        
        # Calculate the interest and total repayment
        interest_rate = loan_product.interest_rate
        loan_yield = (principal_amount * interest_rate / Decimal(100)).quantize(Decimal("0.01"))
        total_repayment = (principal_amount + loan_yield).quantize(Decimal("0.01"))
        
        # Calculate loan due date
        due_date = timezone.now().date() + timedelta(days=loan_product.loan_duration)
        outstanding_balance = instance.outstanding_balance
        # Generate loan ID (ensure uniqueness)
        loan_id = f"FLN-{instance.pk:05}" if instance.pk else f"FLN-{FlexiCashLoanApplication.objects.count() + 1:05}"
        
        # Create the FlexiCashLoanApplication instance
        loan_application = FlexiCashLoanApplication(
            member=member,
            loan_product=loan_product,
            principal_amount=principal_amount,
            interest_rate=interest_rate,
            loan_yield=loan_yield,
            total_repayment=total_repayment,
            loan_status='Pending',  # Loan starts in 'Pending' status
            loan_due_date=due_date,
            loan_id=loan_id,
            outstanding_balance = outstanding_balance 
        )
     
    
        
        # Save the FlexiCashLoanApplication instance
        loan_application.save()

        # Optionally log for debugging
        print(f"FlexiCashLoanApplication created: {loan_application.loan_id}")
        
        
# @receiver(post_save, sender=Transaction)
# def handle_loan_repayment(sender, instance, created, **kwargs):
#     if created and instance.transaction_type == 'Repayment':
#         member = instance.member
#         loan = instance.loan

#         # Update Member's balance by subtracting repayment amount
#         member.balance -= instance.amount
#         member.save()

#         # Update loan balance in MemberLoanApplication
#         loan.loan_balance -= instance.amount
#         if loan.loan_balance <= Decimal('0.00'):
#             loan.loan_balance = Decimal('0.00')
#             loan.payment_complete = True  # Set to True if fully repaid
#             # Close the FlexiCashLoanApplication status if fully repaid
#             flexi_loan = FlexiCashLoanApplication.objects.filter(member=member, loan_product=loan.loan_product).first()
#             if flexi_loan:
#                 flexi_loan.loan_status = 'Closed'
#                 flexi_loan.save()
#         loan.save()

@receiver(post_save, sender=Transaction)
def handle_loan_repayment(sender, instance, created, **kwargs):
    if created and instance.transaction_type == 'Repayment':
        member = instance.member
        loan = instance.loan

        # Update Member's balance by subtracting repayment amount
        member.balance -= instance.amount
        member.save()

        # Update loan balance in MemberLoanApplication
        loan.loan_balance -= instance.amount
        if loan.loan_balance <= Decimal('0.00'):
            loan.loan_balance = Decimal('0.00')
            loan.payment_complete = True  # Set to True if fully repaid
            # Close the FlexiCashLoanApplication status if fully repaid
            flexi_loan = FlexiCashLoanApplication.objects.filter(member=member, loan_product=loan.loan_product).first()
            if flexi_loan:
                flexi_loan.loan_status = 'Closed'
                flexi_loan.save()
        loan.save()
        
