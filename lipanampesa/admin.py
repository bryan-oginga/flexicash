from django.contrib import admin
from .models import LoanMpesaTransaction

@admin.register(LoanMpesaTransaction)
class LoanMpesaTransactionAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ('invoice_id', 'phone_number', 'email', 'amount', 'state', 'created_at')
    list_display_links = ('invoice_id', 'phone_number')
    list_filter = ('state', 'created_at')
    search_fields = ('invoice_id', 'phone_number', 'email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Invoice Details', {
            'fields': ('invoice_id', 'state')
        }),
        ('Customer Information', {
            'fields': ('phone_number', 'email')
        }),
        ('Payment Details', {
            'fields': ('amount', 'narrative', 'created_at')
        }),
    )
