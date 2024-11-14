from django.contrib import admin
from .models import LoanMpesaTransaction

class LoanMpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ('invoice_id', 'phone_number', 'amount', 'state', 'email', 'created_at')  # Display key fields
    list_filter = ('state', 'amount')  # Add filters for easy sorting
    search_fields = ('invoice_id', 'phone_number', 'email')  # Enable search by invoice ID, phone number, and email
    ordering = ('-created_at',)  # Default ordering by the created date (newest first)
    date_hierarchy = 'created_at'  # Add date hierarchy for easy navigation
    readonly_fields = ('invoice_id', 'phone_number', 'email', 'amount', 'narrative', 'state')  # Make fields read-only if needed
    list_per_page = 20  # Display a maximum of 20 records per page
    
    def save_model(self, request, obj, form, change):
        # Optionally, you can add custom behavior when saving a model, such as auto-filling or logging
        if not obj.invoice_id:  # Ensure invoice_id is set before saving
            obj.invoice_id = f"INV-{obj.pk}"  # Example: Generate an invoice ID based on the primary key
        super().save_model(request, obj, form, change)

# Register the model with the custom admin
admin.site.register(LoanMpesaTransaction, LoanMpesaTransactionAdmin)
