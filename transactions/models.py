from django.db import models
from fleximembers.models import FlexiCashMember
from loanapplication.models import MemberLoanApplication
from datetime import timezone

# Create your models here.
class Transaction(models.Model):
    member = models.ForeignKey(FlexiCashMember, on_delete=models.CASCADE, related_name="transactions")
    loan = models.ForeignKey(MemberLoanApplication, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=15,default="Repayment")
    narrative = models.CharField(max_length=15,null=True,blank=True)
    status = models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')], default='PENDING')
    date = models.DateTimeField(auto_now_add=True)
    repayment_type = models.CharField(max_length=20, choices=[('Full', 'Full'), ('Partial', 'Partial')])
    
  

    def __str__(self):
        return f"Loan: {self.transaction_type} of {self.amount} on {self.date} for {self.member}"
    
    class Meta:
        verbose_name = "Loan Transaction"
        verbose_name_plural = "Loan Transactions"
        ordering = ['-date']


    
class LoanStatement(models.Model):
    member = models.ForeignKey(FlexiCashMember, on_delete=models.CASCADE, related_name="statements")
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="statement_entries")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Loan statement: {self.transaction.transaction_type} of {self.transaction.amount} on {self.date} for {self.member}"

    class Meta:
        verbose_name = "Loan Statement"
        verbose_name_plural = "Loan Statements"
        ordering = ['-date']
