from django.http import HttpResponse
from fleximembers.models import FlexiCashMember
from loanapplication.models import MemberLoanApplication, Transaction
from decimal import Decimal
from django.utils import timezone

def repay_loan_handler(request, session_id, phone_number, text):
    parts = text.split('*')
    member = FlexiCashMember.objects.filter(phone=phone_number).first()

    if member:
        # First, ask for repayment option
        if len(parts) == 1:
            response = "CON Please select repayment option:\n1. Full payment\n2. Partial payment"
        
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
                    # Create transaction record
                    Transaction.objects.create(member=member, loan=loan, amount=loan.loan_balance, transaction_type="Repayment")
                    response = "END Your loan has been fully repaid. Thank you!"
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
                    if amount > loan.loan_balance:
                        response = f"END Amount exceeds the loan balance. Remaining balance: {loan.loan_balance}."
                    else:
                        # Create transaction record
                        Transaction.objects.create(member=member, loan=loan, amount=amount, transaction_type="Repayment")
                        response = f"END Partial repayment of {amount} has been received. Remaining balance is {loan.loan_balance}."
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
