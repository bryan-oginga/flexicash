from django.contrib import admin
from .models import MemberLoanApplication

@admin.register(MemberLoanApplication)
class MemberLoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_id', 'member', 'loan_product', 'principal_amount', 
                    'interest_rate', 'loan_status', 'applied_on', 'due_date', 
                    'outstanding_balance', 'total_repayment', 'payment_complete')
    list_filter = ('loan_status', 'applied_on', 'due_date', 'payment_complete')
    search_fields = ('application_id', 'member__first_name', 'member__last_name', 
                     'member__membership_number', 'loan_product__name')
    readonly_fields = ('application_id', 'applied_on','due_date','loan_product','principal_amount','interest_rate','loan_status','outstanding_balance','total_repayment','loan_yield',)
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

