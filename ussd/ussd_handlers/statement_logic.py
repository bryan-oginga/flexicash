from transactions.models import Transaction
from datetime import timedelta
from django.utils import timezone

def get_transactions(member, period):
    """
    Retrieve transactions for the given period (in months).
    """
    # Calculate the start date for the requested period
    start_date = timezone.now() - timedelta(days=period * 30)
    
    # Fetch transactions for the given member and period
    return Transaction.objects.filter(
        member=member,
        state='COMPLETE',
        date__gte=start_date
    ).order_by('date')

def generate_statement_rows(transactions):
    """
    Generate the statement rows directly from transaction data.
    """
    statement_rows = []
    for transaction in transactions:
        # Generate a simple row for each transaction type (Disbursement or Repayment)
        description = 'Disbursement' if transaction.transaction_type == 'Disbursement' else 'Repayment'
        statement_rows.append({
            'date': transaction.date.strftime('%Y-%m-%d'),  # format date
            'amount': transaction.amount,
            'description': description
        })
    return statement_rows
