from django.db import models
from fleximembers.models import FlexiCashMember
from loanapplication.models import MemberLoanApplication


class MpesaTransaction(models.Model):
    merchant_request_id = models.CharField(max_length=255,null=True, blank=True)  
    checkout_request_id = models.CharField(max_length=255,null=True, blank=True)  
    amount = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True) 
    phone_number = models.CharField(max_length=15,null=True, blank=True)  
    result_code = models.IntegerField(null=True, blank=True)   
    result_desc = models.CharField(max_length=255,null=True, blank=True)  
    mpesa_receipt_number = models.CharField(max_length=255, null=True, blank=True)  
    transaction_date = models.DateTimeField(null=True, blank=True)  
    status = models.CharField(max_length=20, default='Pending',null=True, blank=True) 
    callback_url = models.URLField(max_length=500,null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"Payment {self.merchant_request_id} - {self.status}"

    class Meta:
        verbose_name = 'M-Pesa Payment'
        verbose_name_plural = 'M-Pesa Payments'




    
    
    
