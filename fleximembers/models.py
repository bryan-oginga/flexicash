from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta
from decimal import Decimal
import logging

class FlexiCashMember(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    pin = models.CharField(max_length=10)
    member_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    membership_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    loan_limit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('500.00'))
    credit_score = models.IntegerField(default=50)

    def set_loan_limit_based_on_credit_score(self):
        if self.credit_score >= 80:
            self.loan_limit = Decimal('3000.00')
        elif 50 <= self.credit_score < 80:
            self.loan_limit = Decimal('1000.00')
        else:
            self.loan_limit = Decimal('500.00')
        self.save()

    def save(self, *args, **kwargs):
        if not self.membership_number:
            self.membership_number = f"FCM-{self.pk:05}" if self.pk else f"FCM-{FlexiCashMember.objects.count() + 1:05}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.membership_number}"

    class Meta:
        verbose_name = "FlexiCash Member"
        verbose_name_plural = "FlexiCash Members"