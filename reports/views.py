from django.shortcuts import render
from fleximembers.models import FlexiCashMember
from loanapplication.models import MemberLoanApplication
from transactions.models import Transaction
from django.db.models import Sum,Q,Count
from datetime import datetime

def FlexicashDashboard(request):
    # Get today's date
    today = datetime.today().date()
    
    # Active borrowers
    registered_borrowers = FlexiCashMember.objects.all().count()
    active_borrowers = int(registered_borrowers)
    
    # Total loans disbursed
    total_loans_disbursed = MemberLoanApplication.objects.filter(Q(loan_status='Disbursed')|Q(loan_status='Closed')).\
        aggregate(Sum('principal_amount')).get('principal_amount__sum', 0)
    
    if total_loans_disbursed is None:
        total_loans_disbursed = 0
     
    # Total payments received (with 'COMPLETE' state)
    payment_received = Transaction.objects.filter(state='COMPLETE') \
        .aggregate(Sum('amount')).get('amount__sum', 0)
    
    if payment_received is None:
        payment_received = 0
        
    top_customers = MemberLoanApplication.objects.filter(loan_status='Closed')\
        .values('member', 'member__first_name', 'member__last_name','member__phone','member__loan_limit','member__membership_number')\
        .annotate(closed_loans_count=Count('id')).order_by('-closed_loans_count')[:5]  
# Example Output
    for customer in top_customers:
        print(f"Member: {customer['member__first_name']} {customer['member__last_name']}, Closed Loans: {customer['closed_loans_count']}")
    
    loan_profits = MemberLoanApplication.objects.filter(loan_status='COMPLETE')\
        .aggregate(Sum('loan_yield')).get('loan_yield__sum', 0)
    
    # Total past due loans (loans past due and with outstanding balance)
    past_due_loans = MemberLoanApplication.objects.filter(
        loan_status="Disbursed",
        due_date__lt=today,  # Check if the due date is before today
        outstanding_balance__gt=0
    ).aggregate(Sum('outstanding_balance')).get('outstanding_balance__sum', 0)
    
    latest_transactions = Transaction.objects.all()[:6]
    # If no past due loans, ensure past_due_loans is 0, not None
    if past_due_loans is None:
        past_due_loans = 0
        
    if loan_profits is None:
        loan_profits = 0

    # Prepare context for rendering
    context = {
        'registered_borrowers': active_borrowers,
        'total_loans_disbursed': total_loans_disbursed,
        'payment_received': payment_received,
        'past_due_loans': past_due_loans,
        'loan_profits' : loan_profits,
        'latest_transactions' : latest_transactions
        
    }

    # Return the rendered template
    return render(request, 'dashboard.html', context)
