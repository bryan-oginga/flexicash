from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db import models
from django.utils import timezone
# from member.models import FlexiCashMember

class LoanType(models.Model):
    BUSINESS = 'Bussiness Loan'
    PERSONAL = 'Personal Loan'
    EMERGENCY = 'Emergency Loan'
    
    
    
    LOAN_TYPE_CHOICES = [
        (BUSINESS, 'Bussiness Loan'),
        (PERSONAL, 'Personal Loan'),
        (EMERGENCY, 'Emergency Loan'),
    ]
    
    LOAN_DURATION_CHOICES = [
              
         (7, 'One Week'),
         (30, 'One Month'),
         (90,'3 Months')
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
        ('REJECTED', 'Rejected')
    ]
    loan_id = models.CharField(max_length=15, unique=True, blank=True, null=True)  # Auto-generated loan ID field
    member = models.ForeignKey('member.FlexiCashMember', on_delete=models.CASCADE, related_name="loan_applications")
    loan_type = models.ForeignKey('LoanType', on_delete=models.PROTECT, related_name="loan_applications")
    amount_requested = models.DecimalField(max_digits=10, decimal_places=2)
    application_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    interest_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_repayment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    application_date = models.DateTimeField(auto_now_add=True) 
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_date = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True, null=True, help_text="Optional comments by admin")
    payment_complete = models.BooleanField(default=False)
    loan_due_date = models.DateField(null=True, blank=True)
    loan_duration = models.PositiveIntegerField(null=True, blank=True)
    

    
    def disburse_loan(self):
        """ Method to disburse the loan amount to the member's balance """
        if self.status == 'APPROVED' and not self.disbursed_on:
            self.member.balance += self.amount_requested
            self.member.save()
            self.disbursed_on = timezone.now()
            self.save()

    def approve(self):
        """Approve the loan application and set the approval date."""
        self.status = 'APPROVED'
        self.approval_date = timezone.now()
        self.save()
    
    def reject(self, reason=None):
        """Reject the loan application, set the rejection date, and optionally add a comment."""
        self.status = 'REJECTED'
        self.rejection_date = timezone.now()
        if reason:
            self.comments = reason
        self.save()

    def __str__(self):
        return f"Loan Application {self.id} - {self.loan_type.name} for {self.member}"

    class Meta:
        verbose_name = "Loan Application"
        verbose_name_plural = "Loan Applications"
        ordering = ['-application_date']



@receiver(pre_save, sender=LoanApplication)
def set_loan_id(sender, instance, **kwargs):
    """Auto-generate the loan identifier before saving."""
    if not instance.loan_id:
        # Find the next available loan identifier (e.g., FCL-001, FCL-002, ...)
        last_loan = LoanApplication.objects.filter(loan_id__startswith='FCL-').order_by('-id').first()
        if last_loan:
            # Extract the last number and increment by 1
            last_number = int(last_loan.loan_id.split('-')[1])
            next_number = last_number + 1
        else:
            # If no loans exist, start from 1
            next_number = 1
        instance.loan_id = f"FCL-{next_number:03}"  # Format with leading zeros (e.g., FCL-001)
