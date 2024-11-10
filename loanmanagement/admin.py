from django.contrib import admin
from .models import LoanProduct, FlexiCashLoanApplication
from django.utils.html import format_html

# Customizing LoanProduct admin view
class LoanProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'interest_rate', 'loan_duration', 'description')
    list_filter = ('loan_duration', 'name')
    search_fields = ('name', 'description')
    ordering = ['name']
    
    # Optional: Custom display for loan types
    def display_name(self, obj):
        return format_html(f"<strong>{obj.name}</strong>")
    
    display_name.short_description = 'Loan Type'

admin.site.register(LoanProduct, LoanProductAdmin)


# Customizing FlexiCashLoanApplication admin view
class FlexiCashLoanApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'loan_id', 'member', 'loan_product', 'requested_amount', 'loan_status',
        'application_date', 'approval_date', 'loan_due_date', 'interest_rate', 'interest_amount', 'total_repayment', 'loan_profit'
    )
    list_filter = ('loan_status', 'loan_product', 'application_date', 'loan_due_date')
    search_fields = ('loan_id', 'member__first_name', 'member__last_name', 'loan_product__name')
    ordering = ['-application_date']
    
    # Optional: Make some fields read-only
    readonly_fields = ('loan_id', 'interest_amount', 'total_repayment', 'loan_profit')
    
    # Optionally, you can add actions to process loans
    def approve_loan(self, request, queryset):
        for loan in queryset:
            loan.loan_status = 'Approved'
            loan.save()

    approve_loan.short_description = "Approve selected loans"

    def reject_loan(self, request, queryset):
        for loan in queryset:
            loan.loan_status = 'Rejected'
            loan.save()

    reject_loan.short_description = "Reject selected loans"

    actions = ['approve_loan', 'reject_loan']
    
admin.site.register(FlexiCashLoanApplication, FlexiCashLoanApplicationAdmin)
