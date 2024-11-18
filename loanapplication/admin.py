from django.contrib import admin
from .models import LoanProduct, MemberLoanApplication
import logging

@admin.register(LoanProduct)
class LoanProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'interest_rate', 'loan_duration', 'description')
    search_fields = ('name',)
    list_filter = ('loan_duration',)
    ordering = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'interest_rate', 'loan_duration')
        }),
        ('Additional Information', {
            'fields': ('description',),
            'classes': ('collapse',),
        }),
    )


@admin.register(MemberLoanApplication)
class MemberLoanApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'application_ref', 'member', 'loan_product', 
        'principal_amount', 'loan_status', 'application_date', 
        'due_date', 'payment_complete'
    )
    search_fields = ('application_ref', 'member__name', 'loan_product__name')
    list_filter = ('loan_status', 'loan_product', 'payment_complete')
    ordering = ('-application_date',)
    readonly_fields = ('application_ref', 'application_date','application_date', 'outstanding_balance', 'loan_yield', 'total_repayment')
    fieldsets = (
        ('Loan Application Details', {
            'fields': ('application_ref', 'member', 'loan_product', 'principal_amount', 'interest_rate', 'outstanding_balance','loan_yield','loan_status')
        }),
        ('Repayment Information', {
            'fields': ('due_date','total_repayment', 'loan_penalty',),
            'classes': ('collapse',),
        }),
        ('Dates and Status', {
            'fields': ('application_date', 'disbursement_date', 'payment_complete'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        """
        Customize queryset to prefetch related data for better performance in list display.
        """
        qs = super().get_queryset(request)
        return qs.select_related('member', 'loan_product')


# Optional: Register logging for admin actions
logger = logging.getLogger(__name__)
