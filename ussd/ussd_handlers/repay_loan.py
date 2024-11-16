from django.http import HttpResponse
from fleximembers.models import FlexiCashMember
from loanapplication.models import MemberLoanApplication
from transactions.models import Transaction
from decimal import Decimal
from lipanampesa.utils import initiate_stk_push  # Import the function to trigger STK Push
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

    if member:
        # Format phone number
        # First, ask for repayment option
        if len(parts) == 1:
            response = "CON Please select repayment option:\n1. Full Payment\n2. Partial Payment"
        
        # If "Full payment" is selected, ask for PIN
        elif len(parts) == 2 and parts[1] == "1":
            response = "CON Enter your PIN to confirm full repayment."
        
        # If "Partial payment" is selected, ask for amount
        elif len(parts) == 2 and parts[1] == "2":
            response = "CON Enter amount for partial repayment:"
        
        # If PIN is entered for full repayment
        elif len(parts) == 3 and parts[1] == "1":
            amount = Decimal(parts[1])
            pin = parts[2]
            if pin == member.pin:
                loan = MemberLoanApplication.objects.filter(member=member, payment_complete=False).first()
                if loan:
                    # Initiate STK Push for full repayment
                    response = f"END STK Push has been initiated successfully."
                    stk_response = service.collect.mpesa_stk_push(phone_number='254799043853',
                                  email="joe@doe.com", amount=10, narrative="Purchase")

                    # Check if STK Push initiation was successful
                    invoice_id = stk_response['invoice']['invoice_id']
                    if invoice_id:
                        # Create transaction record
                        Transaction.objects.create(
                            member=member, 
                            loan=loan, 
                            amount=loan.outstanding_balance, 
                            transaction_type="Repayment",
                            repayment_type = "Full"
                            
                        )
                        response = "END Your loan has been fully repaid. Thank you! STK Push initiated, awaiting confirmation."
                    else:
                        response = "END Payment initiation failed. Please try again."

                else:
                    response = "END No active loan found for repayment."
            else:
                response = "END Incorrect PIN. Please try again."
        
        # If amount is entered for partial repayment
        elif len(parts) == 3 and parts[1] == "2":
            amount = Decimal(parts[2])
            response = f"CON Enter your PIN to confirm partial repayment of {amount}."
        
        # If PIN and amount are entered for partial repayment
        elif len(parts) == 4 and parts[1] == "2":
            amount = Decimal(parts[2])
            pin = parts[3]
            if pin == member.pin:
                loan = MemberLoanApplication.objects.filter(member=member, payment_complete=False).first()
                if loan:
                    # Ensure repayment doesn't exceed loan balance
                    if amount > loan.outstanding_balance:
                        response = f"END Amount exceeds the loan balance. Remaining balance: {loan.outstanding_balance}."
                    else:
                        # Initiate STK Push for partial repayment
                        response = f"END STK Push has been initiated successfully."
                        stk_response  = service.collect.mpesa_stk_push(phone_number='254799043853',
                                  email="joe@doe.com", amount=10, narrative="Purchase")

                        # Check if STK Push initiation was successful
                        invoice_id = stk_response['invoice']['invoice_id']
                        if invoice_id:
                            # Create transaction record
                            Transaction.objects.create(
                                member=member, 
                                loan=loan, 
                                amount=amount, 
                                transaction_type="Repayment",
                                repayment_type = "Partial"

                            )
                            response = f"END Partial repayment of {amount} has been received. Remaining balance is {loan.outstanding_balance}."
                        else:
                            response = "END Payment initiation failed. Please try again."
                else:
                    response = "END No active loan found for repayment."
            else:
                response = "END Incorrect PIN. Please try again."

        # If no valid option is selected
        else:
            response = "END Invalid option. Please try again."

    else:
        response = "END Member not found. Please register first."

    return HttpResponse(response, content_type="text/plain")