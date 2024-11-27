from django.db import models
from fleximembers.models import FlexiCashMember
from loanapplication.models import MemberLoanApplication
class MPesaTransaction(models.Model):
    # member = models.ForeignKey(FlexiCashMember, on_delete=models.CASCADE, related_name="transactions")
    # loan = models.ForeignKey(MemberLoanApplication, on_delete=models.CASCADE, related_name="transactions")
    # transaction_type = models.CharField(max_length=15,choices=[('Repayment', 'Repayment'), ('Disbursemnt', 'Disbursemnt')],default="Repayment")
    # repayment_type = models.CharField(max_length=20, choices=[('Full', 'Full'), ('Partial', 'Partial')])
    external_reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    channel_id = models.IntegerField()
    provider = models.CharField(max_length=50, default="m-pesa")
    status = models.CharField(max_length=50, null=True, blank=True)
    checkout_request_id = models.CharField(max_length=100, null=True, blank=True)
    mpesa_receipt_number = models.CharField(max_length=100, null=True, blank=True)
    result_code = models.IntegerField(null=True, blank=True)
    result_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.external_reference} - {self.status}"
    
    
    
