from django.db import models
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal


class FlexiCashMember(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    pin = models.CharField(max_length=10)  # Simplified PIN storage for debugging
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    membership_number = models.CharField(max_length=50, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Only auto-generate membership number if it doesn't exist
        if not self.membership_number:
            super().save(*args, **kwargs)  # Save to generate primary key
            self.membership_number = f"FM-{str(self.pk).zfill(3)}"
            super().save(update_fields=['membership_number'])
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.membership_number}"

    def get_absolute_url(self):
        return reverse('member_detail', args=[str(self.pk)])

    class Meta:
        verbose_name = "FlexiCash Member"
        verbose_name_plural = "FlexiCash Members"


class MemberLoan(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REPAID', 'Repaid'),
        ('DEFAULTED', 'Defaulted')
    ]

    member = models.ForeignKey('FlexiCashMember', on_delete=models.CASCADE, related_name="loans")
    loan_type = models.ForeignKey('loan.LoanType', on_delete=models.PROTECT, related_name="loans")
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Principal loan amount
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    duration = models.PositiveIntegerField(help_text="Duration in months")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    applied_on = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    loan_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    interest_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_repayment = models.DecimalField(max_digits=10, decimal_places=2,  default=0.00)

    def save(self, *args, **kwargs):
        # Set applied_on to current time if it's not already set
        if not self.applied_on:
            self.applied_on = timezone.now()
        
        # Only calculate on the first save
        if not self.pk:  
            self.interest_rate = Decimal(self.loan_type.interest_rate)
            self.amount = Decimal(self.amount)
            self.loan_balance = self.amount
            
            # Calculate interest amount based on principal and interest rate
            self.interest_amount = self.amount * self.interest_rate / Decimal(100)
            
            # Calculate total repayment amount
            self.total_repayment = self.amount + self.interest_amount

            # Ensure consistent data type for loan_balance calculation
            self.loan_balance = self.amount + self.interest_amount

            # Calculate due date based on loan type
            if self.loan_type.name == "Emergency Loan":
                self.due_date = self.applied_on + timedelta(weeks=1)
            elif self.loan_type.name == "Personal Loan":
                self.due_date = self.applied_on + timedelta(days=30)
            elif self.loan_type.name == "Business Loan":  # Corrected "Bussiness" to "Business"
                self.due_date = self.applied_on + timedelta(days=90)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.loan_type.name} for {self.member} - {self.amount} at {self.interest_rate}%"


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('DISBURSEMENT', 'Disbursement'),
        ('REPAYMENT', 'Repayment'),
        ('PENALTY', 'Penalty')
    ]
    member = models.ForeignKey('FlexiCashMember', on_delete=models.CASCADE, related_name="transactions")
    loan = models.ForeignKey('MemberLoan', on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=15, choices=TRANSACTION_TYPE_CHOICES)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.create_statement_entry()

    def create_statement_entry(self):
        # Avoid duplicate entries in the statement table for the same transaction
        if not Statement.objects.filter(member=self.member, loan=self.loan, date=self.date, amount=self.amount).exists():
            Statement.objects.create(
                member=self.member,
                loan=self.loan,
                amount=self.amount,
                transaction_type=self.transaction_type,
                description=f"{self.get_transaction_type_display()} for loan ID {self.loan.id}"
            )


class Statement(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('REPAYMENT', 'Repayment'),
        ('DISBURSEMENT', 'Disbursement'),
        ('PENALTY', 'Penalty'),
        ('FEE', 'Fee'),
    ]

    member = models.ForeignKey('FlexiCashMember', on_delete=models.CASCADE, related_name="statements")
    loan = models.ForeignKey('MemberLoan', on_delete=models.CASCADE, related_name="statements")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=15, choices=TRANSACTION_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True, help_text="Additional details about the transaction")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} for Loan {self.loan.id} by {self.member} on {self.date.strftime('%Y-%m-%d')}"
