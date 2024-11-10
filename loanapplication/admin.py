from django.contrib import admin
from .models import MemberLoanApplication, Transaction, LoanStatement

# MemberLoanApplication Admin
@admin.register(MemberLoanApplication)
class MemberLoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_id', 'member', 'loan_product', 'requested_amount', 'loan_status', 'applied_on', 'due_date', 'loan_balance', 'interest_amount', 'total_repayment', 'payment_complete')
    list_filter = ('loan_status', 'loan_product', 'payment_complete')
    search_fields = ('application_id', 'member__first_name', 'member__last_name', 'loan_product__name')
    ordering = ('-applied_on',)
    readonly_fields = ('application_id', 'interest_amount', 'total_repayment')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # If the object already exists (in edit mode), make 'application_id' readonly
            return self.readonly_fields + ('member', 'loan_product')
        return self.readonly_fields

# Transaction Admin
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('loan', 'member', 'transaction_type', 'amount', 'date')
    list_filter = ('transaction_type', 'date')
    search_fields = ('loan__application_id', 'member__first_name', 'member__last_name')
    ordering = ('-date',)
    readonly_fields = ('loan', 'member', 'transaction_type', 'amount')

# LoanStatement Admin
@admin.register(LoanStatement)
class LoanStatementAdmin(admin.ModelAdmin):
    list_display = ('member', 'transaction', 'date')
    list_filter = ('date',)
    search_fields = ('member__first_name', 'member__last_name', 'transaction__loan__application_id')
    ordering = ('-date',)
    readonly_fields = ('member', 'transaction', 'date')
