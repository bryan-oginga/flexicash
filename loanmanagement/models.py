from django.db import models
from decimal import Decimal
from fleximembers.models import FlexiCashMember
from datetime import timedelta
from loanapplication.models import MemberLoanApplication
import datetime
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
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
        ('Disbursed', 'Disbursed'),
        ('Rejected', 'Rejected'),
        ('Closed', 'Closed'),  # Added to handle closed loans
    ]
    
    loan_id = models.CharField(max_length=15, unique=True, blank=True, null=True)
    member = models.ForeignKey(FlexiCashMember, on_delete=models.CASCADE, related_name="loan_applications")
    loan_product = models.ForeignKey(LoanProduct, on_delete=models.PROTECT, related_name="loan_applications")
    principal_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Loan amount requested
    loan_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    application_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True, blank=True,editable=False)
    loan_due_date = models.DateField(null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    loan_yield = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_repayment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    outstanding_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    loan_penalty = models.DecimalField(default=0.00,null=True,blank=True,decimal_places=2,max_digits=10)

    
    def save(self, *args, **kwargs):
        if not self.loan_id:
            # Generate loan_id when saving the loan application
            self.loan_id = f"FLN-{self.pk:05}" if self.pk else f"FLN-{FlexiCashLoanApplication.objects.count() + 1:05}" 
        if self.loan_status == "Disbursed":
            self.approval_date = datetime.datetime.now()
            self.loan_due_date = self.approval_date + timedelta(days=self.loan_product.loan_duration)
            self.outstanding_balance = self.total_repayment
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Loan Application {self.loan_id} - {self.loan_product.name} for {self.member}"

    class Meta:
        verbose_name = "Manage Loan Application"
        verbose_name_plural = "Manage Loan Applications"
        ordering = ['-application_date']


@receiver(post_save,sender=FlexiCashLoanApplication)
def update_loan_application_balance(sender,instance,**kwargs):
    if instance.loan_status == 'Disbursed':
       member = instance.member 
       try:
           loan = MemberLoanApplication.objects.get(member=member)
           print("This is the balance : ",loan.outstanding_balance)
           loan.outstanding_balance = instance.total_repayment
           loan.save()
       except MemberLoanApplication.DoesNotExist:
           print("The loan does not exits : ",loan.outstanding_balance)

           
               
       