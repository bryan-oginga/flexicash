from django.db import models
from decimal import Decimal
from member.models import FlexiCashMember  # Assuming this is the correct model for FlexiCashMember

class LoanType(models.Model):
    BUSINESS = 'Business Loan'
    PERSONAL = 'Personal Loan'
    EMERGENCY = 'Emergency Loan'
    
    LOAN_TYPE_CHOICES = [
        (BUSINESS, 'Business Loan'),
        (PERSONAL, 'Personal Loan'),
        (EMERGENCY, 'Emergency Loan'),
    ]
    
    LOAN_DURATION_CHOICES = [
        (7, 'One Week'),
        (30, 'One Month'),
        (90, '3 Months'),
    ]
    
    name = models.CharField(max_length=20, choices=LOAN_TYPE_CHOICES, unique=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Interest rate for the loan type")
    loan_duration = models.PositiveIntegerField(choices=LOAN_DURATION_CHOICES, help_text="Duration of the loan")
    description = models.TextField(blank=True, null=True, help_text="Description of the loan type")
    max_loan_amount = models.DecimalField(max_digits=12, decimal_places=2, default=50000, help_text="Maximum loan amount for this loan type")

    def __str__(self):
        return self.get_name_display()

    class Meta:
        verbose_name = "Loan Type"
        verbose_name_plural = "Loan Types"


class LoanApplication(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Repaid', 'Repaid'),
        ('Defaulted', 'Defaulted'),
        ('Disbursed', 'Disbursed'),
        ('Rejected', 'Rejected'),
    ]
    
    loan_id = models.CharField(max_length=15, unique=True, blank=True, null=True)
    member = models.ForeignKey(FlexiCashMember, on_delete=models.CASCADE, related_name="loan_applications")
    loan_type = models.ForeignKey(LoanType, on_delete=models.PROTECT, related_name="loan_applications")
    amount_requested = models.DecimalField(max_digits=10, decimal_places=2)  # Loan amount requested
    loan_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    application_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    loan_due_date = models.DateField(null=True, blank=True)
    payment_complete = models.BooleanField(default=False)
    loan_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    interest_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_repayment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    loan_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    loan_duration = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Override the save method to calculate loan profit and total repayment
        before saving the loan application.
        """
        if not self.loan_id:
            self.loan_id = f"FCL-{str(self.pk).zfill(4)}"  # Generate loan ID if not set
        
        # Calculate interest amount and total repayment based on amount requested and interest rate
        if self.requested_amount and self.interest_rate is not None:
            self.interest_amount = self.requested_amount * self.interest_rate / Decimal(100)
            self.total_repayment = self.requested_amount + self.interest_amount
            self.loan_profit = self.total_repayment - self.requested_amount
        else:
            # Handle case where values might be missing (optional)
            self.interest_amount = Decimal('0.00')
            self.total_repayment = Decimal('0.00')
            self.loan_profit = Decimal('0.00')

        # Setting loan balance to the total repayment
        self.loan_balance = self.total_repayment

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Loan Application {self.loan_id} - {self.loan_type.name} for {self.member}"

    class Meta:
        verbose_name = "Loan Application"
        verbose_name_plural = "Loan Applications"
        ordering = ['-application_date']
