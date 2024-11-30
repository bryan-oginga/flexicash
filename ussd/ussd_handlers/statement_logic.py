from transactions.models import Transaction
from datetime import timedelta
from django.utils import timezone

def get_transactions(member, period):
    """Retrieve transactions based on the given period in months."""
    start_date = timezone.now() - timedelta(days=period * 30)
    # Ensure we're querying for actual model instances
    transactions = Transaction.objects.filter(
        member=member,
        state='COMPLETE',
        date__gte=start_date
    ).order_by('date')

    # Log each transaction to ensure they're model instances
    for transaction in transactions:
        print(f"Transaction: {transaction} | Type: {type(transaction)}")

    return transactions  # Return the queryset of actual model instances


def generate_statement_rows(transactions):
    """Generate statement rows from the provided transaction model instances."""
    statement_rows = []
    for transaction in transactions:
        # Ensure that each transaction is an instance of Transaction
        if isinstance(transaction, Transaction):
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
        else:
            print(f"Unexpected type encountered: {type(transaction)}")

    return statement_rows

