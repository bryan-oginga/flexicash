from django.contrib import admin
from .models import MPesaTransaction

@admin.register(MPesaTransaction)
class MPesaTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'external_reference', 
        'amount', 
        'phone_number', 
        'channel_id', 
        'provider', 
        'status', 
        'mpesa_receipt_number', 
        'created_at'
    )
    list_filter = ('status', 'provider', 'created_at', 'updated_at')
    search_fields = ('external_reference', 'phone_number', 'mpesa_receipt_number', 'checkout_request_id')
    readonly_fields = ('created_at', 'updated_at', 'checkout_request_id', 'mpesa_receipt_number', 'result_code', 'result_description')
    ordering = ('-created_at',)  # Order by most recent transactions first
    list_per_page = 20  # Paginate transactions for better performance
    fieldsets = (
        (None, {
            'fields': ('external_reference', 'amount', 'phone_number', 'channel_id', 'provider', 'status')
        }),
        ('Transaction Details', {
            'fields': ('checkout_request_id', 'mpesa_receipt_number', 'result_code', 'result_description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
