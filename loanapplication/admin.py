from django.contrib import admin
from .models import MemberLoanApplication, Transaction, LoanStatement

@admin.register(MemberLoanApplication)
class MemberLoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_id', 'member', 'loan_product', 'principal_amount', 
                    'interest_rate', 'loan_status', 'applied_on', 'due_date', 
                    'outstanding_balance', 'total_repayment', 'payment_complete')
    list_filter = ('loan_status', 'applied_on', 'due_date', 'payment_complete')
    search_fields = ('application_id', 'member__first_name', 'member__last_name', 
                     'member__membership_number', 'loan_product__name')
    readonly_fields = ('application_id', 'applied_on')
    date_hierarchy = 'applied_on'
    ordering = ['-applied_on']
    fieldsets = (
        ("Loan Details", {
            'fields': ('application_id', 'member', 'loan_product', 'principal_amount', 
                       'interest_rate', 'loan_status', 'due_date')
        }),
        ("Financial Info", {
            'fields': ('outstanding_balance', 'loan_yield', 'total_repayment', 'payment_complete')
        }),
    )

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

@admin.register(LoanStatement)
class LoanStatementAdmin(admin.ModelAdmin):
    list_display = ('member', 'transaction', 'date')
    list_filter = ('date',)
    search_fields = ('member__first_name', 'member__last_name', 
                     'transaction__transaction_type', 'transaction__amount')
    ordering = ['-date']
    date_hierarchy = 'date'
