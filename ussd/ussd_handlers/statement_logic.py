from transactions.models import Transaction
from datetime import timedelta
from django.utils import timezone

def get_transactions(member, period):
    """Retrieve transactions based on the given period in months."""
    start_date = timezone.now() - timedelta(days=period * 30)
    return Transaction.objects.filter(
        member=member,
        state='COMPLETE',
        date__gte=start_date
    ).order_by('date')

def generate_statement_rows(transactions):
    """Generate rows for the statement with dynamic balance calculation."""
    balance = 0
    statement_rows = []

    for transaction in transactions:
        if transaction.transaction_type == 'Disbursement':
            balance += transaction.amount
        elif transaction.transaction_type == 'Repayment':
            balance -= transaction.amount

        statement_rows.append({
            'date': transaction.date,
            'description': transaction.repayment_type if transaction.transaction_type == 'Repayment' else 'Disbursement',
            'amount': transaction.amount,
            'balance': balance
        })

    return statement_rows
