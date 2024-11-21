from django.db import models

class MPesaTransaction(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('QUEUED', 'Queued'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    TRANSACTION_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]
    
    external_reference = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    channel_id = models.IntegerField()
    checkout_request_id = models.CharField(max_length=255, null=True, blank=True)
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default="QUEUED")
    result_code = models.IntegerField(null=True, blank=True)
    mpesa_receipt_number = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, choices=TRANSACTION_STATUS_CHOICES, default="PENDING")
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Transaction {self.external_reference} - {self.status}"

    class Meta:
        db_table = 'tiny_pesa_transactions'
        managed = True
        verbose_name = 'Mpesa Payment'
        verbose_name_plural = 'Mpesa Payments'
