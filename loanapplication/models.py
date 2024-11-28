from django.db import models
from fleximembers.models import FlexiCashMember
from django.core.exceptions import ValidationError
from datetime import timedelta
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class LoanProduct(models.Model):
    LOAN_PRODUCT_CHOICES = [
        ('Business Loan', 'Business Loan'),
        ('Personal Loan', 'Personal Loan'),
        ('Emergency Loan', 'Emergency Loan'),
    ]
    
    LOAN_DURATION_CHOICES = [
        (7, '1 Week'),
        (30, '1 Month'),
        (90, '3 Months'),
    ]
    
    INTEREST_RATE_CHOICES = [
        (10, '10% Interest Rate'),
        (20, '20 % Interest Rate'),
        (30, '30 % Interest Rate'),
    ]
    
    name = models.CharField(max_length=20,null=True,choices=LOAN_PRODUCT_CHOICES)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2,choices=INTEREST_RATE_CHOICES,help_text="Interest rate for the loan type")
    loan_duration = models.PositiveIntegerField(choices=LOAN_DURATION_CHOICES, help_text="Duration of the loan in days")
    description = models.TextField(blank=True, null=True,help_text="Description of the loan type")

    def __str__(self):
        return self.get_name_display()

    class Meta:
        verbose_name = "Loan Product"
        verbose_name_plural = "Loan Products"
        
 
class MemberLoanApplication(models.Model):
    LOAN_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Closed', 'Closed'),
        ('Active', 'Active'),
    ]

    application_ref = models.CharField(max_length=15, unique=True, null=True, blank=True)
    member = models.ForeignKey(FlexiCashMember, on_delete=models.CASCADE, related_name="loans")
    loan_product = models.ForeignKey(LoanProduct, on_delete=models.PROTECT, related_name="loans")
    principal_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Principal loan amount
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    loan_status = models.CharField(max_length=20, choices=LOAN_STATUS_CHOICES, default='Pending')
    application_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    outstanding_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    loan_yield = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_repayment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_complete = models.BooleanField(default=False,null=True, blank=True)
    loan_penalty = models.DecimalField(default=0.00,null=True,blank=True,decimal_places=2,max_digits=10)
    disbursement_date = models.DateTimeField(null=True, blank=True)

    def clean(self):
        # Validate requested amount does not exceed loan limit
        if self.principal_amount > self.member.loan_limit:
            raise ValidationError("Requested amount exceeds the member's loan limit.")

    def save(self, *args, **kwargs):
    # Generate application_ref only once
        if not self.application_ref:
            self.application_ref = f"FLP-{self.pk:05}" if self.pk else f"FLP-{MemberLoanApplication.objects.count() + 1:05}"
    
    # Set disbursement date details
        if self.loan_status == "Approved":
            if not self.disbursement_date:
                self.disbursement_date = datetime.today().date()  # Ensure disbursement_date is set
                    
        if self.disbursement_date and not self.due_date:
            self.due_date = self.disbursement_date + timedelta(days=self.loan_product.loan_duration)
    
        super().save(*args, **kwargs)

        
    def __str__(self):
        return f"{self.loan_product.name} for {self.member} - {self.principal_amount} at {self.interest_rate}%"

    class Meta:
        verbose_name = "Loan  Application"
        verbose_name_plural = "Loan Applications"
        ordering = ['-application_date']