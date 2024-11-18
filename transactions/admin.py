from django.contrib import admin
from .models import Transaction

# Register your models here.
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('member', 'loan', 'amount', 'transaction_type', 'status', 
                    'date', 'repayment_type', 'narrative')
    list_filter = ('status', 'transaction_type', 'repayment_type', 'date')
    search_fields = ('member__first_name', 'member__last_name', 
                     'loan__application_id', 'narrative')
    readonly_fields = ('date',)
    ordering = ['-date']
    date_hierarchy = 'date'

