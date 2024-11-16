from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.db.models import F
from decimal import Decimal
from .models import Transaction
from loanapplication.models import MemberLoanApplication
from loanmanagement.models import FlexiCashLoanApplication
from fleximembers.models import FlexiCashMember
from django.db.models import Case, When, Value


@receiver(post_save, sender=Transaction)
def handle_loan_balance(sender, instance, created, **kwargs):
    if created and instance.transaction_type == 'Repayment':
        member = instance.member
        loan = instance.loan
        amount = instance.amount
        repayment_type = instance.repayment_type

        with transaction.atomic():
            # Full Repayment
            if repayment_type == 'Full':
                # Update member balance
                member.member_balance = Decimal('0.00')
                member.save()

                # Update FlexiCashLoan balance
                flexi_loan = FlexiCashLoanApplication.objects.filter(
                    member=member, loan_product=loan.loan_product
                ).first()
                if flexi_loan:
                    flexi_loan.outstanding_balance = Decimal('0.00')
                    flexi_loan.loan_status = 'Closed'
                    flexi_loan.save()

                # Update Loan Application balance
                loan.outstanding_balance = Decimal('0.00')
                loan.payment_complete = True
                loan.save()

            # Partial Repayment
            elif repayment_type == 'Partial':
                # Update member balance
                member.member_balance = F('member_balance') - amount
                member.save()

                # Update FlexiCashLoan balance
                flexi_loan = FlexiCashLoanApplication.objects.filter(
                    member=member, loan_product=loan.loan_product
                ).first()
                if flexi_loan:
                    flexi_loan.outstanding_balance = F('outstanding_balance') - amount
                    flexi_loan.loan_status = Case(When(outstanding_balance__lte=0, then=Value('Closed')),default=Value(flexi_loan.loan_status),)
                    flexi_loan.save()

                # Update Loan Application balance
                loan.outstanding_balance = Case(
                    When(outstanding_balance__lte=Decimal('0.00'), then=Value(Decimal('0.00'))),
                    default=F('outstanding_balance') - amount
                )
                loan.payment_complete = Case(
                    When(outstanding_balance=Decimal('0.00'), then=Value(True)),
                    default=Value(False)
                )
                loan.save()

            # Refresh balances after F() updates
            member.refresh_from_db()
            loan.refresh_from_db()
            if flexi_loan:
                flexi_loan.refresh_from_db()
