from transactions.models import Transaction
from datetime import timedelta
from django.utils import timezone
from datetime import timedelta
from datetime import datetime
def generate_statement_rows(transactions):
    """
    Generate rows for the statement with date, description, amount paid, and balance.
    """
    statement_rows = []
    balance = 0

    for transaction in transactions:
        if transaction.transaction_type == 'Disbursement':
            balance += transaction.amount
            description = 'Loan Disbursement'
        elif transaction.transaction_type == 'Repayment':
            balance -= transaction.amount
            description = 'Loan Repayment'
        
        statement_rows.append({
            'date': transaction.date.strftime('%Y-%m-%d'),
            'description': description,
            'amount_paid': transaction.amount,
            'balance': balance,
        })
    
    return statement_rows

def get_transactions(member, period):
    """
    Get transactions for a member for the given period (in months).
    """
    period_start_date = datetime.now() - timedelta(days=period * 30)
    transactions = Transaction.objects.filter(member=member, date__gte=period_start_date)
    return transactions
