from django.db import models
from fleximembers.models import FlexiCashMember
from loanapplication.models import MemberLoanApplication


class MpesaTransaction(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Success", "Success"),
        ("Failed", "Failed"),
    ]

    merchant_request_id = models.CharField(max_length=255, db_index=True)
    checkout_request_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    result_code = models.IntegerField()
    result_desc = models.CharField(max_length=255)
    mpesa_receipt_number = models.CharField(max_length=255, unique=True, null=True, blank=True)
    transaction_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    callback_url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.merchant_request_id} - {self.status}"

    class Meta:
        verbose_name = "M-Pesa Payment"
        verbose_name_plural = "M-Pesa Payments"
        indexes = [
            models.Index(fields=["merchant_request_id", "transaction_date"]),
        ]


    def __str__(self):
        return f"Payment {self.merchant_request_id} - {self.status}"

    class Meta:
        verbose_name = 'M-Pesa Payment'
        verbose_name_plural = 'M-Pesa Payments'




    
    
    
