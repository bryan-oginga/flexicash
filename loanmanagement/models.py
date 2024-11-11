from django.db import models
from decimal import Decimal
from fleximembers.models import FlexiCashMember
from datetime import timedelta


class LoanProduct(models.Model):
    loan_product_CHOICES = [
        ('Business Loan', 'Business Loan'),
        ('Personal Loan', 'Personal Loan'),
        ('Emergency Loan', 'Emergency Loan'),
    ]
    
    LOAN_DURATION_CHOICES = [
        (7, '1 Week'),
        (30, '1 Month'),
        (90, '3 Months'),
    ]
    
    name = models.CharField(max_length=20, choices=loan_product_CHOICES)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Interest rate for the loan type")
    loan_duration = models.PositiveIntegerField(choices=LOAN_DURATION_CHOICES, help_text="Duration of the loan in days")
    description = models.TextField(blank=True, null=True, help_text="Description of the loan type")

    def __str__(self):
        return self.get_name_display()

    class Meta:
        verbose_name = "Loan Product"
        verbose_name_plural = "Loan Products"


class FlexiCashLoanApplication(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Repaid', 'Repaid'),
        ('Defaulted', 'Defaulted'),
        ('Disbursed', 'Disbursed'),
        ('Rejected', 'Rejected'),
        ('Closed', 'Closed'),  # Added to handle closed loans
    ]
    
    loan_id = models.CharField(max_length=15, unique=True, blank=True, null=True)
    member = models.ForeignKey(FlexiCashMember, on_delete=models.CASCADE, related_name="loan_applications")
    loan_product = models.ForeignKey(LoanProduct, on_delete=models.PROTECT, related_name="loan_applications")
    requested_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Loan amount requested
    loan_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    application_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    loan_due_date = models.DateField(null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    interest_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_repayment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    loan_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def save(self, *args, **kwargs):
        if not self.loan_id:
            # Generate loan_id when saving the loan application
            self.loan_id = f"FLN-{self.pk:05}" if self.pk else f"FLN-{FlexiCashLoanApplication.objects.count() + 1:05}"
        
        super().save(*args, **kwargs)


    
    def __str__(self):
        return f"Loan Application {self.loan_id} - {self.loan_product.name} for {self.member}"

    class Meta:
        verbose_name = "FlexiCash Loan Application"
        verbose_name_plural = "FlexiCash Loan Applications"
        ordering = ['-application_date']