from django.http import HttpResponse
from member.models import FlexiCashMember, MemberLoan, Transaction
from decimal import Decimal

def repay_loan_handler(request, session_id, phone_number, text):
    parts = text.split('*')
    member = FlexiCashMember.objects.filter(phone=phone_number).first()

    if member:
        # Initial prompt for repayment type
        if len(parts) == 1:
            response = "CON Please select repayment option:\n1. Full payment\n2. Partial payment"
            return HttpResponse(response, content_type="text/plain")

        # Full or partial payment option selected
        elif len(parts) == 2:
            option = parts[1]
            if option == "1":  # Full payment
                response = "CON Enter your PIN to confirm full repayment."
            elif option == "2":  # Partial payment
                response = "CON Enter amount for partial repayment:"
            else:
                response = "END Invalid option selected."
            return HttpResponse(response, content_type="text/plain")

        # For full payment: Confirm PIN and process payment
        elif len(parts) == 3 and parts[1] == "1":
            pin = parts[2]
            if pin == member.pin:
                # Process full payment
                loan = MemberLoan.objects.filter(member=member, payment_complete=False).first()
                if loan:
                    loan.loan_balance = 0
                    loan.payment_complete = True
                    loan.save()
                    # Update member balance and create transaction record
                    member.balance -= loan.total_repayment
                    member.save()
                    Transaction.objects.create(member=member, loan=loan, amount=loan.total_repayment, transaction_type="Repayment")
                    response = "END Your loan has been fully repaid. Thank you!"
                else:
                    response = "END No active loan found for repayment."
            else:
                response = "END Incorrect PIN. Please try again."
            return HttpResponse(response, content_type="text/plain")

        # For partial payment: Enter amount and confirm PIN
        elif len(parts) == 3 and parts[1] == "2":
            amount = parts[2]
            response = f"CON Enter your PIN to confirm partial repayment of {amount}."
            return HttpResponse(response, content_type="text/plain")

        elif len(parts) == 4 and parts[1] == "2":
            amount = Decimal(parts[2])
            pin = parts[3]
            if pin == member.pin:
                # Process partial payment
                loan = MemberLoan.objects.filter(member=member, payment_complete=False).first()
                if loan:
                    loan.loan_balance -= amount
                    loan.payment_complete = loan.loan_balance <= 0
                    loan.save()
                    # Update member balance and create transaction record
                    member.balance -= amount
                    member.save()
                    Transaction.objects.create(member=member, loan=loan, amount=amount, transaction_type="Repayment")
                    response = f"END Partial repayment of {amount} has been received. Remaining balance is {loan.loan_balance}."
                else:
                    response = "END No active loan found for repayment."
            else:
                response = "END Incorrect PIN. Please try again."
            return HttpResponse(response, content_type="text/plain")

    else:
        return HttpResponse("END Member not found. Please register first.", content_type="text/plain")
