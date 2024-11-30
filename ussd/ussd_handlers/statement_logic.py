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
    statement_rows = []
    for transaction in transactions:
        # Use dictionary key access instead of attribute access
        if transaction.get('transaction_type') == 'Disbursement':
            # Process disbursement
            statement_rows.append({
                'date': transaction.get('date'),
                'amount': transaction.get('amount'),
                'description': transaction.get('description', 'Disbursement'),
            })
        elif transaction.get('transaction_type') == 'Repayment':
            # Process repayment
            statement_rows.append({
                'date': transaction.get('date'),
                'amount': transaction.get('amount'),
                'description': transaction.get('description', 'Repayment'),
            })
    return statement_rows
