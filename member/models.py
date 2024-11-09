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
    member = models.ForeignKey('FlexiCashMember', on_delete=models.CASCADE, related_name="loans")
    loan_type = models.ForeignKey('loan.LoanType', on_delete=models.PROTECT, related_name="loans")
    requested_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Principal loan amount
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    duration = models.PositiveIntegerField(help_text="Duration in months")
    status = models.CharField(max_length=20, default='Pending')
    applied_on = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    loan_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    interest_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_repayment = models.DecimalField(max_digits=10, decimal_places=2,  default=0.00)
    payment_complete = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.applied_on:
            self.applied_on = timezone.now()

        if not self.pk:  
            self.interest_rate = Decimal(self.loan_type.interest_rate)
            self.requested_amount = Decimal(self.requested_amount)
            self.loan_balance = self.requested_amount

            self.interest_amount = self.requested_amount * self.interest_rate / Decimal(100)
            self.total_repayment = self.requested_amount + self.interest_amount
            self.loan_balance = self.requested_amount + self.interest_amount

            if self.loan_type.name == "Emergency Loan":
                self.due_date = self.applied_on + timedelta(weeks=1)
            elif self.loan_type.name == "Personal Loan":
                self.due_date = self.applied_on + timedelta(days=30)
            elif self.loan_type.name == "Business Loan":
                self.due_date = self.applied_on + timedelta(days=90)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.loan_type.name} for {self.member} - {self.requested_amount} at {self.interest_rate}%"


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

