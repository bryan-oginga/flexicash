from django.db import models
from fleximembers.models import FlexiCashMember
from loanapplication.models import MemberLoanApplication
from datetime import timezone

# Create your models here.
class Transaction(models.Model):
    invoice_id = models.CharField(max_length=100, unique=True,blank=True)
    phone_number = models.CharField(max_length=20,blank=True,null=True) 
    member = models.ForeignKey(FlexiCashMember, on_delete=models.CASCADE, related_name="transactions")
    loan = models.ForeignKey(MemberLoanApplication, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=15,choices=[('Repayment', 'Repayment'), ('Disbursemnt', 'Disbursemnt')],default="Repayment")
    narrative = models.CharField(max_length=15,null=True,blank=True)
    state = models.CharField(max_length=20, default='PENDING')
    date = models.DateTimeField(auto_now_add=True)
    repayment_type = models.CharField(max_length=20, choices=[('Full', 'Full'), ('Partial', 'Partial')])
    email = models.EmailField(null=True,blank=True)  

    
  

    def __str__(self):
        return f"Loan: {self.transaction_type} of {self.amount} on {self.date} for {self.member}"
    
    class Meta:
        verbose_name = "M-PESA Transaction"
        verbose_name_plural = "M-PESA Transactions"
        ordering = ['-date']


    
    