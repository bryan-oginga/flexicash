from django.db import models
from django.utils import timezone

# Create your models here.
class MpesaTransaction(models.Model):
    CheckoutRequestID = models.CharField(max_length=50, blank=True, null=True)
    MerchantRequestID = models.CharField(max_length=20, blank=True, null=True)
    ResultCode = models.IntegerField(blank=True, null=True)
    ResultDesc = models.CharField(max_length=120, blank=True, null=True)
    Amount = models.FloatField(blank=True, null=True)
    MpesaReceiptNumber = models.CharField(max_length=15, blank=True, null=True)
    TransactionDate = models.DateTimeField(blank=True, null=True)
    PhoneNumber = models.CharField(max_length=13, blank=True, null=True)
    
    
    def save(self, *args, **kwargs):
        if not self.TransactionDate.tzinfo:
            self.TransactionDate = timezone.make_aware(self.date, timezone.get_current_timezone())
        super(MpesaTransaction, self).save(*args, **kwargs)

    def __str__(self):
        return f"Loan: {self.MpesaReceiptNumber} of {self.Amount} on {self.TransactionDate} "
    

