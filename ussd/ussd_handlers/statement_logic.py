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
        # Access attributes directly
        if transaction.transaction_type == 'Disbursement':
            # Process disbursement
            statement_rows.append({
                'date': transaction.date,
                'amount': transaction.amount,
                'description': 'Disbursement',
            })
        elif transaction.transaction_type == 'Repayment':
            # Process repayment
            statement_rows.append({
                'date': transaction.date,
                'amount': transaction.amount,
                'description': 'Repayment',
            })
    return statement_rows

