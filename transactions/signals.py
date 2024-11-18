from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.db.models import F
from decimal import Decimal
from .models import Transaction
from loanapplication.models import MemberLoanApplication
from fleximembers.models import FlexiCashMember
from django.db.models import Case, When, Value,DecimalField,BooleanField


@receiver(post_save, sender=Transaction)
def handle_loan_balance(sender, instance, created, **kwargs):
    if created and instance.transaction_type == 'Repayment':
        member = instance.member
        loan = instance.loan
        amount = Decimal(instance.amount)
        repayment_type = instance.repayment_type

        with transaction.atomic():
            # Full Repayment
            if repayment_type == 'Full':
                # Update member balance
                member.member_balance = Decimal('0.00')
                print("This is the member balance : ",member.member_balance)
                member.save()

                # Update Loan Application balance
                loan.outstanding_balance = Decimal('0.00')
                loan.payment_complete = True
                loan.loan_status = 'Closed'
                loan.save()

            # Partial Repayment
            elif repayment_type == 'Partial':
                
                member.member_balance = F('member_balance') - amount
                member.save()

                # Update Loan Application balance
                loan.outstanding_balance = max(loan.outstanding_balance - amount, Decimal('0.00'))

                # Update Loan status and payment completion
                if loan.outstanding_balance == Decimal('0.00'):
                    loan.payment_complete = True
                    loan.loan_status = 'Closed'
                else:
                    loan.payment_complete = False
                    loan.loan_status = 'Pending'

                loan.save()
               
        
                       
            member.refresh_from_db()
            loan.refresh_from_db()
           