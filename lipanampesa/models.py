from django.db import models

class LoanMpesaTransaction(models.Model):
    invoice_id = models.CharField(max_length=100, unique=True,blank=True)  # Unique invoice ID from IntaSend
    phone_number = models.CharField(max_length=20,unique=True,blank=True)  # Customer phone number
    email = models.EmailField()  # Customer email
    amount = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)  # Amount for the payment
    narrative = models.CharField(max_length=255,null=True,blank=True)  # Narrative for the payment
    state = models.CharField(max_length=20, default='PENDING')  # The state of the invoice (e.g., "PENDING", "COMPLETED")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        # Combine both loan and invoice information in a clear representation
        return f"Loan of {self.amount} KES for {self.phone_number} (Invoice ID: {self.invoice_id}, State: {self.state})"
    
    class  Meta:
        db_table = ''
        managed = True
        verbose_name = 'Mpesa Payment'
        verbose_name_plural = 'Mpesa Payments'


  