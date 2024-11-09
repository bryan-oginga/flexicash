from django.http import HttpResponse
from loan.models import LoanType, LoanApplication
from member.models import FlexiCashMember,MemberLoan,Transaction

def apply_loan_handler(request, session_id, phone_number, text):
    parts = text.split('*')
    member = FlexiCashMember.objects.filter(phone=phone_number).first()

    if member:
        # If the user hasn't selected a loan type yet, show available loan types
        if len(parts) == 1:
            loan_types = LoanType.objects.all()
            response = "CON Choose a loan type:\n"
            for index, loan in enumerate(loan_types, start=1):
                response += f"{index}. {loan.name}\n"
            return HttpResponse(response, content_type="text/plain")

        # If the user selects a loan type, ask for the loan amount
        elif len(parts) == 2:
            loan_type_index = int(parts[1]) - 1
            loan_types = LoanType.objects.all()
            if loan_type_index < len(loan_types):
                selected_loan_type = loan_types[loan_type_index]
                response = f"CON Enter loan amount for {selected_loan_type.name}:"
                return HttpResponse(response, content_type="text/plain")

        # After loan amount is entered, ask for PIN
        elif len(parts) == 3:
            loan_type_index = int(parts[1]) - 1
            loan_types = LoanType.objects.all()
            if loan_type_index < len(loan_types):
                selected_loan_type = loan_types[loan_type_index]
                requested_amount = parts[2]
                response = f"CON Please enter your PIN to confirm loan of {requested_amount} for {selected_loan_type.name}:"
                return HttpResponse(response, content_type="text/plain")
        
        # If PIN is provided, process loan application
        elif len(parts) == 4:
            pin = parts[3]
            
            # Directly compare the entered PIN with the stored PIN
            if pin == member.pin:
                loan_type_index = int(parts[1]) - 1
                loan_types = LoanType.objects.all()
                if loan_type_index < len(loan_types):
                    selected_loan_type = loan_types[loan_type_index]
                    requested_amount = parts[2]

                    # Validate if amount is numeric
                    if not requested_amount.isdigit():
                        return HttpResponse("END Invalid loan amount. Please enter a numeric value.", content_type="text/plain")
                    
                    # Save the loan application
                    loan_application = MemberLoan(
                        member=member,
                        loan_type=selected_loan_type,
                        requested_amount=requested_amount,
                        duration=selected_loan_type.loan_duration,  # Set loan duration; you can calculate dynamically
                    )
                    loan_application.save()

                    response = f"END Your loan of {requested_amount} for {selected_loan_type.name} has been successfully submitted. Please wait as we process your application."
                    return HttpResponse(response, content_type="text/plain")
            else:
                return HttpResponse("END Incorrect PIN. Please try again.", content_type="text/plain")
    
    else:
        return HttpResponse("END Member not found. Please register first.", content_type="text/plain")
