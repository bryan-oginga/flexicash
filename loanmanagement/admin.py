from django.contrib import admin
from .models import LoanProduct, FlexiCashLoanApplication

@admin.register(LoanProduct)
class LoanProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'interest_rate', 'loan_duration', 'description_snippet')
    search_fields = ('name',)
    list_filter = ('name', 'loan_duration')
    ordering = ['name']
    fieldsets = (
        ("Loan Product Details", {
            'fields': ('name', 'interest_rate', 'loan_duration', 'description')
        }),
    )

    def description_snippet(self, obj):
        return obj.description[:50] + "..." if obj.description and len(obj.description) > 50 else obj.description
    description_snippet.short_description = "Description"

@admin.register(FlexiCashLoanApplication)
class FlexiCashLoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'member', 'loan_product', 'principal_amount', 
                    'loan_status', 'application_date', 'approval_date', 
                    'loan_due_date', 'outstanding_balance', 'total_repayment')
    list_filter = ('loan_status', 'application_date', 'loan_due_date', 'approval_date')
    search_fields = ('loan_id', 'member__first_name', 'member__last_name', 
                     'member__membership_number', 'loan_product__name')
    readonly_fields = ('loan_id', 'application_date')
    date_hierarchy = 'application_date'
    ordering = ['-application_date']
    fieldsets = (
        ("Loan Details", {
            'fields': ('loan_id', 'member', 'loan_product', 'principal_amount', 
                       'loan_status', 'application_date', 'approval_date', 'loan_due_date')
        }),
        ("Financial Information", {
            'fields': ('interest_rate', 'loan_yield', 'total_repayment', 
                       'outstanding_balance', 'loan_penalty')
        }),
    )
