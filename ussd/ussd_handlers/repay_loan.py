from django.http import HttpResponse
from fleximembers.models import FlexiCashMember
from loanapplication.models import MemberLoanApplication,LoanProduct
from transactions.models import Transaction
from decimal import Decimal
# from lipanampesa.utils import initiate_stk_push  # Import the function to trigger STK Push
from django.utils import timezone
import logging

from django.http import JsonResponse
from intasend import APIService
import logging
from django.conf import settings

# Initialize IntaSend APIService with sandbox/test mode enabled
service = APIService(token=settings.INSTASEND_SECRET_KEY, 
                     publishable_key=settings.INSTASEND_PUBLISHABLE_KEY, 
                     test=True)


def repay_loan_handler(request, session_id, phone_number, text):
    parts = text.split('*')
    member = FlexiCashMember.objects.filter(phone=phone_number).first()

    if not member:
        return HttpResponse("END Member not found. Please register first.", content_type="text/plain")

    if len(parts) == 1:
        return HttpResponse("CON Please select repayment option:\n1. Full Payment\n2. Partial Payment", content_type="text/plain")

    elif len(parts) == 2:
        if parts[1] == "1":
            return HttpResponse("CON Enter your PIN to confirm full repayment.", content_type="text/plain")
        elif parts[1] == "2":
            return HttpResponse("CON Enter amount for partial repayment:", content_type="text/plain")

    elif len(parts) == 3:
        if parts[1] == "1":  # Full Repayment
            pin = parts[2]
            if pin != member.pin:
                return HttpResponse("END Incorrect PIN. Please try again.", content_type="text/plain")

            loan = MemberLoanApplication.objects.filter(member=member, payment_complete=False).first()
            if not loan:
                return HttpResponse("END No active loan found for repayment.", content_type="text/plain")

            if member.member_balance == Decimal('0.00'):
                return HttpResponse(f"END Amount exceeds your loan balance of: {loan.outstanding_balance}.", content_type="text/plain")

            # Initiate STK Push
            stk_response = service.collect.mpesa_stk_push(
                phone_number='254799043853',
                email=member.email,
                amount=float(loan.outstanding_balance),  # Ensure float for STK API
                narrative=loan.application_ref
            )

            # Check response
            if "invoice" in stk_response and "invoice_id" in stk_response["invoice"]:
                Transaction.objects.create(
                    member=member,
                    loan=loan,
                    amount=loan.outstanding_balance,
                    transaction_type="Repayment",
                    repayment_type="Full"
                )
                return HttpResponse("END Your loan has been fully repaid. Thank you! Awaiting confirmation.", content_type="text/plain")

            return HttpResponse("END Payment initiation failed. Please try again.", content_type="text/plain")

        elif parts[1] == "2":  # Partial Repayment
            amount = Decimal(parts[2])
            return HttpResponse(f"CON Enter your PIN to confirm partial repayment of {amount}.", content_type="text/plain")

    elif len(parts) == 4 and parts[1] == "2":
        amount = Decimal(parts[2])
        pin = parts[3]
        if pin != member.pin:
            return HttpResponse("END Incorrect PIN. Please try again.", content_type="text/plain")

        loan = MemberLoanApplication.objects.filter(member=member, payment_complete=False).first()
        if not loan:
            return HttpResponse("END No active loan found for repayment.", content_type="text/plain")

        if amount > loan.outstanding_balance:
            return HttpResponse(f"END Amount exceeds the loan balance. Remaining balance: {loan.outstanding_balance}.", content_type="text/plain")

        # Initiate STK Push
        stk_response = service.collect.mpesa_stk_push(
            phone_number='254799043853',
            amount=float(amount),
            narrative=loan.application_ref
        )

        # Check response
        if "invoice" in stk_response and "invoice_id" in stk_response["invoice"]:
            Transaction.objects.create(
                member=member,
                loan=loan,
                amount=amount,
                transaction_type="Repayment",
                repayment_type="Partial",
                narrative=stk_response["invoice"]["invoice_id"],
                status=stk_response["invoice"].get("state", "Pending")
            )
            return HttpResponse(f"END Partial repayment of {amount} has been received. Remaining balance is {loan.outstanding_balance - amount}.", content_type="text/plain")

        return HttpResponse("END Payment initiation failed. Please try again.", content_type="text/plain")

    return HttpResponse("END Invalid option. Please try again.", content_type="text/plain")
