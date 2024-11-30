from transactions.models import Transaction
from datetime import timedelta
from django.utils import timezone

def get_transactions(member, period):
    """Retrieve transactions based on the given period in months."""
    start_date = timezone.now() - timedelta(days=period * 30)
    # Ensure this query returns Transaction model instances
    return Transaction.objects.filter(
        member=member,
        state='COMPLETE',
        date__gte=start_date
    ).order_by('date')

def generate_statement_rows(transactions):
    statement_rows = []
    for transaction in transactions:
        # Ensure that transaction is a model instance and has the attribute `transaction_type`
        if transaction.transaction_type == 'Disbursement':
            statement_rows.append({
                'date': transaction.date,
                'amount': transaction.amount,
                'description': 'Disbursement',
            })
        elif transaction.transaction_type == 'Repayment':
            statement_rows.append({
                'date': transaction.date,
                'amount': transaction.amount,
                'description': 'Repayment',
            })
    return statement_rows
