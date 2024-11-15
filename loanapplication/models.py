from django.db import models
from fleximembers.models import FlexiCashMember
from django.core.exceptions import ValidationError
from datetime import timedelta
from decimal import Decimal
import logging
from decimal import Decimal
from django.utils import timezone

logger = logging.getLogger(__name__)

class MemberLoanApplication(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Disbursed', 'Disbursed'),
        ('Rejected', 'Rejected'),
        ('Completed', 'Completed')
    ]

    application_id = models.CharField(max_length=15, unique=True, null=True, blank=True)
    member = models.ForeignKey(FlexiCashMember, on_delete=models.CASCADE, related_name="loans")
    loan_product = models.ForeignKey('loanmanagement.LoanProduct', on_delete=models.PROTECT, related_name="loans")
    principal_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Principal loan amount
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    loan_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_on = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    outstanding_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    loan_yield = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_repayment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_complete = models.BooleanField(default=False)
    loan_penalty = models.DecimalField(default=0.00,null=True,blank=True,decimal_places=2,max_digits=10)


    def save(self, *args, **kwargs):
        if not self.application_id:
            self.application_id = f"FLP-{self.pk:05}" if self.pk else f"FLP-{MemberLoanApplication.objects.count() + 1:05}"
        
           
        super().save(*args, **kwargs)

    def clean(self):
        # Validate requested amount does not exceed loan limit
        if self.principal_amount > self.member.loan_limit:
            raise ValidationError("Requested amount exceeds the member's loan limit.")

    def __str__(self):
        return f"{self.loan_product.name} for {self.member} - {self.principal_amount} at {self.interest_rate}%"
    
    class Meta:
        verbose_name = "MemberLoan Loan Application"
        verbose_name_plural = "Member Loan Applications"
        ordering = ['-applied_on']

class Transaction(models.Model):
    member = models.ForeignKey(FlexiCashMember, on_delete=models.CASCADE, related_name="transactions")
    loan = models.ForeignKey(MemberLoanApplication, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=15,default="Repayment")
    narrative = models.CharField(max_length=15,null=True,blank=True)
    status = models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')], default='PENDING')
    date = models.DateTimeField(default=timezone.now)
    repayment_type = models.CharField(max_length=20, choices=[('Full Payment', 'Full'), ('Partial', 'Partial Payment')])
    
    def save(self, *args, **kwargs):
        if not self.date.tzinfo:
            self.date = timezone.make_aware(self.date, timezone.get_current_timezone())
        super(Transaction, self).save(*args, **kwargs)

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
        verbose_name = "Mini Statement"
        verbose_name_plural = "MIni Statements"
        ordering = ['-date']
