from django.contrib import admin
from .models import MpesaPayment

class MpesaPaymentAdmin(admin.ModelAdmin):
    list_display = ('merchant_request_id', 'checkout_request_id', 'phone_number', 'amount', 'status', 'transaction_date', 'created_at', 'updated_at')
    list_filter = ('status', 'result_code', 'transaction_date', 'created_at')
    search_fields = ('merchant_request_id', 'checkout_request_id', 'phone_number', 'mpesa_receipt_number', 'transaction_desc')
    ordering = ('-created_at',)
    date_hierarchy = 'transaction_date'
    readonly_fields = ('merchant_request_id', 'checkout_request_id', 'transaction_desc', 'result_code', 'result_desc', 'mpesa_receipt_number', 'transaction_date', 'status', 'callback_url', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('merchant_request_id', 'checkout_request_id', 'transaction_desc', 'result_code', 'result_desc', 'mpesa_receipt_number')
        }),
        ('Payment Details', {
            'fields': ('amount', 'phone_number', 'status', 'callback_url', 'transaction_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    # Optionally, you can customize the list view with inline editing (e.g., for batch updating)
    # inlines = []

admin.site.register(MpesaPayment, MpesaPaymentAdmin)
