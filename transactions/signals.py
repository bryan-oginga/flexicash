from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from .models import LoanStatement,Transaction
from loanapplication.models import MemberLoanApplication
from loanmanagement.models import FlexiCashLoanApplication
from fleximembers.models import FlexiCashMember
from decimal import Decimal


        
@receiver(post_save,sender=Transaction)
def handle_loan_balance(instance,created,**kwargs):
    if created and instance.transaction_type == 'Repayment':
        member = instance.member
        loan = instance.loan
        amount = instance.amount
        repayment_type = instance.repayment_type
        # total_repayment = loan.total_repayment
        outstanding_balance = loan.outstanding_balance
        
        if repayment_type == 'Full':
            
            #update member balance
            member.member_balance = 0
            member.save()
            
            #update Floxloan  balance
            flexi_loan = FlexiCashLoanApplication.objects.filter(member=member, loan_product=loan.loan_product).first()
            if flexi_loan:
                flexi_loan.outstanding_balance = 0
                if flexi_loan.outstanding_balance <= Decimal('0.00'):
                    flexi_loan.outstanding_balance = Decimal('0.00')
                    flexi_loan.loan_status = 'Closed'  # Set to True if fully repaid
                flexi_loan.save()
                
            #update  loan application balance 
            loan.outstanding_balance = 0
            if loan.outstanding_balance <= Decimal('0.00'):
                loan.outstanding_balance = Decimal('0.00')
                loan.payment_complete = True  # Set to True if fully repaid
            loan.save()
        
        else:
            member.member_balance -= amount
            member.save()
            
            #update Floxloan  balance
            flexi_loan = FlexiCashLoanApplication.objects.filter(member=member, loan_product=loan.loan_product).first()
            if flexi_loan:
                flexi_loan.outstanding_balance -= amount
                if flexi_loan.outstanding_balance <= Decimal('0.00'):
                    flexi_loan.outstanding_balance = Decimal('0.00')
                    flexi_loan.loan_status = 'Closed'  # Set to True if fully repaid
                flexi_loan.save()
                
            #update outstanding_balance 
            outstanding_balance   -= amount
            if outstanding_balance <= Decimal('0.00'):
                outstanding_balance = Decimal('0.00')
                loan.payment_complete = True  # Set to True if fully repaid
            loan.save()
