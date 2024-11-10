from django.http import HttpResponse
from datetime import datetime, timedelta
from member.models import FlexiCashMember, Transaction

def mini_statement_handler(request, session_id, phone_number, text_parts):
    member = FlexiCashMember.objects.filter(phone=phone_number).first()
    if not member:
        return HttpResponse("END Member not found. Please register first.", content_type="text/plain")
    
    # Check if a period was specified
    if len(text_parts) < 2:
        return HttpResponse("END Invalid selection. Please try again.", content_type="text/plain")
    
    # Determine the selected period
    option = text_parts[1]
    if option == "1":
        period = datetime.now() - timedelta(days=30)  # 1 Month
    elif option == "2":
        period = datetime.now() - timedelta(days=90)  # 3 Months
    elif option == "3":
        period = datetime.now() - timedelta(days=180)  # 6 Months
    elif option == "4":
        period = datetime.now() - timedelta(days=365)  # 1 Year
    else:
        return HttpResponse("END Invalid option. Please try again.", content_type="text/plain")
    
    # Retrieve transactions within the specified period
    transactions = Transaction.objects.filter(member=member, date__gte=period).order_by('-date')[:5]  # Limit to 5 recent transactions for brevity
    
    if not transactions:
        response = "END No transactions found for the selected period."
    else:
        # Format the mini statement response
        response = "END Mini Statement:\n"
        for txn in transactions:
            txn_type = txn.transaction_type
            amount = txn.amount
            date = txn.date.strftime('%d %b %Y')
            response += f"{txn_type} - {amount} on {date}\n"
        response += "\nThank you for using FlexiCash."
    
    return HttpResponse(response, content_type="text/plain")
