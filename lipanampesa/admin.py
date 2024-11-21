from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from .models import MPesaTransaction

class MpesaPesaTransactionAdmin(admin.ModelAdmin):
    # Display fields in the list view
    list_display = ('external_reference', 'amount', 'phone_number', 'payment_status_color', 'status', 'initiated_at', 'completed_at')
    
    # Search functionality
    search_fields = ['external_reference', 'phone_number', 'amount']
    
    # Filters
    list_filter = ['payment_status', 'status', 'initiated_at']
    
    # Fieldset to organize the form layout in the admin view
    fieldsets = (
        (None, {
            'fields': ('external_reference', 'amount', 'phone_number', 'channel_id')
        }),
        ('Payment Information', {
            'fields': ('payment_status', 'result_code', 'mpesa_receipt_number', 'status', 'completed_at')
        }),
    )
    
    # Custom display for payment_status in the list view
    def payment_status_color(self, obj):
        """Color code the payment status for easy visibility"""
        if obj.payment_status == 'COMPLETED':
            return format_html('<span style="color: green;">{}</span>', obj.payment_status)
        elif obj.payment_status == 'FAILED':
            return format_html('<span style="color: red;">{}</span>', obj.payment_status)
        elif obj.payment_status == 'QUEUED':
            return format_html('<span style="color: orange;">{}</span>', obj.payment_status)
        return format_html('<span>{}</span>', obj.payment_status)

    payment_status_color.short_description = 'Payment Status'

    # Custom actions: Mark as completed
    def mark_as_completed(self, request, queryset):
        """Custom action to mark payments as completed"""
        updated = queryset.update(status='COMPLETED', completed_at=models.F('initiated_at'))
        self.message_user(request, f'{updated} transactions marked as completed.')

    mark_as_completed.short_description = "Mark selected as completed"
    
    # Add custom actions to the admin panel
    actions = ['mark_as_completed']

# Register the model and custom admin
admin.site.register(MPesaTransaction, MpesaPesaTransactionAdmin)
