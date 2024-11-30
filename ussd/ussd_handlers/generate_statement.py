from django.db.models import Sum
from decimal import Decimal
from transactions.models import Transaction

def generate_loan_statement(member, loan_application):
    """Generates a loan statement based on existing transactions without updating any balance."""
    
    # Query all transactions related to the member and loan
    transactions = Transaction.objects.filter(
        member=member, 
        loan=loan_application
    ).order_by('date')
    
    # Start with the existing outstanding balance from the loan application
    current_balance = loan_application.outstanding_balance
    total_repaid = Decimal('0.00')
    total_disbursed = Decimal('0.00')
    
    # Process each transaction to calculate the total disbursed and total repaid
    for transaction in transactions:
        if transaction.transaction_type == "Disbursement":
            total_disbursed += transaction.amount  # Add disbursement to total disbursed
        elif transaction.transaction_type == "Repayment":
            total_repaid += transaction.amount  # Add repayment to total repaid
    
    # Calculate the current outstanding balance
    current_balance = loan_application.outstanding_balance + total_disbursed - total_repaid
    
    # Create a statement summary
    statement = {
        "member": member,
        "loan_ref": loan_application.application_ref,
        "total_disbursed": total_disbursed,
        "total_repaid": total_repaid,
        "current_balance": current_balance,
        "loan_status": loan_application.loan_status,
        "payment_complete": loan_application.payment_complete
    }
    
    return statement
