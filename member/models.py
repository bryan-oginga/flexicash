from django.db import models
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
from django.urls import reverse
import logging
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

class FlexiCashMember(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    pin = models.CharField(max_length=10)  # Simplified PIN storage for debugging
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    membership_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    loan_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)  # Loan limit based on credit score
    credit_score = models.IntegerField(default=50, null=True, blank=True)  # Credit score to help determine loan limit
    total_repaid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Total amount repaid by the member

    def save(self, *args, **kwargs):
        # Set loan limit based on credit score
        if self.credit_score >= 80:
            self.loan_limit = 50000  # High credit score = higher loan limit
        elif self.credit_score >= 50:
            self.loan_limit = 20000  # Moderate credit score = lower loan limit
        else:
            self.loan_limit = 10000  # Low credit score = minimal loan limit
        super().save(*args, **kwargs)

        # Generate membership number if it does not exist
        if not self.membership_number:
            self.membership_number = f"FM-{str(self.pk).zfill(3)}"
            super().save(update_fields=['membership_number'])

    def get_absolute_url(self):
        return reverse('member_detail', args=[str(self.pk)])

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.membership_number}"

    class Meta:
        verbose_name = "FlexiCash Member"
        verbose_name_plural = "FlexiCash Members"

class MemberLoan(models.Model):
    member = models.ForeignKey(FlexiCashMember, on_delete=models.CASCADE, related_name="loans")
    loan_type = models.ForeignKey('loan.LoanType', on_delete=models.PROTECT, related_name="loans")
    requested_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Principal loan amount
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    duration = models.PositiveIntegerField(help_text="Duration in days", null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending')
    applied_on = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    loan_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    interest_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_repayment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_complete = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # Check if requested_amount or interest_rate is None
        if self.requested_amount is None:
            raise ValidationError("Requested amount cannot be None.")
        if self.interest_rate is None:
            raise ValidationError("Interest rate cannot be None.")
        
        # Perform the calculation only if values are valid
        self.interest_amount = self.requested_amount * self.interest_rate / Decimal(100)
        
        super(MemberLoan, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.pk:  
            self.interest_amount = self.requested_amount * self.interest_rate / Decimal(100)
            self.total_repayment = self.requested_amount + self.interest_amount
            self.loan_balance = self.total_repayment
            self.duration = self.loan_type.loan_duration
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
        ('Disbursement', 'Disbursement'),
        ('Repayment', 'Repayment'),
        ('Withdrawal', 'Withdrawal'),
    ]
    member = models.ForeignKey(FlexiCashMember, on_delete=models.CASCADE, related_name="transactions")
    loan = models.ForeignKey(MemberLoan, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=15, choices=TRANSACTION_TYPE_CHOICES)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logger.info(f"Transaction created for {self.member} - Amount: {self.amount}, Type: {self.transaction_type}")
        self.create_statement_entry()

    def create_statement_entry(self):
        LoanStatement.objects.create(
            member=self.member,
            transaction=self,
            amount=self.amount,
            transaction_type=self.transaction_type,
            date=self.date
        )


class LoanStatement(models.Model):
    member = models.ForeignKey(FlexiCashMember, on_delete=models.CASCADE, related_name="statements")
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="statement_entries")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=15)
    date = models.DateTimeField()

    def __str__(self):
        return f"Loan statement: {self.transaction_type} of {self.amount} on {self.date} for {self.member}"

    class Meta:
        verbose_name = "Statement Entry"
        verbose_name_plural = "Statement Entries"
        ordering = ['-date']
