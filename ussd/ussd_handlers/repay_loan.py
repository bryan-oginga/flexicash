from django.http import HttpResponse
from fleximembers.models import FlexiCashMember
from loanapplication.models import MemberLoanApplication,LoanProduct
from transactions.models import Transaction
from decimal import Decimal
from django.utils import timezone
import logging
from django.http import JsonResponse
from intasend import APIService
import logging
from django.conf import settings

token = settings.INTASEND_SECRET_KEY
publishable_key   = settings.INTASEND_PUBLISHABLE_KEY
service = APIService(token=token, publishable_key=publishable_key)

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
                    if member.member_balance == Decimal('0.00'):
                        response = f"END Amount exceeds your  loan  balance of : {loan.outstanding_balance}."
                    else:
                        response = f"END STK Push has been initiated successfully."
                        
                        member_phone = member.phone.lstrip('+')
                        print("This is the memebers phone number : ",member_phone)
                        member_email = member.email
                        print("This is the members email : ",member_email)
                        
                        stk_response = service.collect.mpesa_stk_push(
                            phone_number='254799043853',
                            # phone_number=member_phone,
                            amount=float(loan.outstanding_balance),
                            narrative=loan.application_ref,
                            email=member.email,
                        )
                        
                        
                        print(stk_response)
                        invoice_id = stk_response['invoice']['invoice_id']
                        amount_paid = stk_response['invoice']['net_amount']
                        state = stk_response['invoice']['state']
                        account = stk_response['invoice']['account']
                        
                        
                        if invoice_id:
                            print("This is the invoice Id : ",invoice_id)
                            Transaction.objects.create(
                                member=member, 
                                loan=loan, 
                                amount=float(amount_paid), 
                                transaction_type="Repayment",
                                repayment_type = "Partial",
                                narrative = invoice_id,
                                state = state,
                                invoice_id= invoice_id,
                                phone_number = account,
                                email = member_email,
                        )
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
                        
                        member_phone = member.phone.lstrip('+')
                        print("This is the memebers phone number : ",member_phone)
                        member_email = member.email
                        print("This is the members email : ",member_email)

                        
                        stk_response = service.collect.mpesa_stk_push(
                            phone_number=member_phone,
                            # phone_number='254799043853',
                            amount=float(amount),
                            narrative=loan.application_ref,
                            email=member_email,
                        )
                        
                        invoice_id = stk_response['invoice']['invoice_id']
                        amount_paid = stk_response['invoice']['net_amount']
                        state = stk_response['invoice']['state']
                        account = stk_response['invoice']['account']
                                               
                        if invoice_id:
                            print("This is the invoice Id : ",invoice_id)
                            # Create transaction record
                            Transaction.objects.create(
                                member=member, 
                                loan=loan, 
                                amount=float(amount_paid), 
                                transaction_type="Repayment",
                                repayment_type = "Partial",
                                narrative = invoice_id,
                                state = state,
                                invoice_id= invoice_id,
                                phone_number = account,
                                email = member_email,
                                     
                            )
                            # response = f"END Partial repayment of {amount} has been received. Remaining balance is {loan.outstanding_balance}."
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