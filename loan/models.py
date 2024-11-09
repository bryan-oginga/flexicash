from django.db import models
from django.utils import timezone
from decimal import Decimal
from member.models import MemberLoan

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
    loan_duration = models.PositiveIntegerField(choices=LOAN_DURATION_CHOICES)
    description = models.TextField(blank=True, null=True, help_text="Description of the loan type")
    max_loan_amount = models.DecimalField(max_digits=12, decimal_places=2, default=100000, help_text="Maximum loan amount for this loan type")

    def __str__(self):
        return self.get_name_display()


class LoanApplication(models.Model):
    STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('APPROVED', 'Approved'),
    ('REPAID', 'Repaid'),
    ('DEFAULTED', 'Defaulted'),
    ('DISBURSED', 'Disbursed')
]
    loan_id = models.CharField(max_length=15, unique=True, blank=True, null=True)
    member = models.ForeignKey('member.FlexiCashMember', on_delete=models.CASCADE, related_name="loan_applications")
    loan_type = models.ForeignKey('loan.LoanType', on_delete=models.PROTECT, related_name="loan_applications")
    amount_requested = models.DecimalField(max_digits=10, decimal_places=2)  # Loan amount requested
    loan_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    application_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    loan_due_date = models.DateField(null=True, blank=True)
    disbursed = models.BooleanField(default=False)
    payment_complete = models.BooleanField(default=False)
    loan_balance = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    interest_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_repayment = models.DecimalField(max_digits=10, decimal_places=2,  default=0.00)
    loan_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    loan_duration = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """Override the save method to update the corresponding MemberLoan status."""
        if self.loan_status in ['APPROVED', 'REJECTED', 'DISBURSED','DEFAULTED','REPAID']:
            # Get or create a MemberLoan instance related to this LoanApplication
            member_loan, created = MemberLoan.objects.get_or_create(
                loan_application=self,
                member=self.member
            )
            # Update the MemberLoan status based on the LoanApplication status
            member_loan.update_status(self.loan_status)
        
        # Call the parent class save method to ensure the LoanApplication is saved as well
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Loan Application {self.id} - {self.loan_type.name} for {self.member}"

    class Meta:
        verbose_name = "Loan Application"
        verbose_name_plural = "Loan Applications"
        ordering = ['-application_date']
