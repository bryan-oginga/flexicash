from django.contrib import admin
from .models import LoanType, LoanApplication

class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'member', 'loan_type', 'amount_requested', 'loan_status', 'application_date', 'loan_due_date', 'total_repayment', 'payment_complete')
    search_fields = ('loan_id', 'member__membership_number', 'loan_type__name', 'loan_status')
    list_filter = ('loan_status', 'loan_type', 'member')
    ordering = ['-application_date']
    date_hierarchy = 'application_date'

    def has_change_permission(self, request, obj=None):
        """
        Prevent editing of loan applications that are already 'Repaid'
        """
        if obj and obj.loan_status == 'Repaid':
            return False
        return super().has_change_permission(request, obj)

admin.site.register(LoanApplication, LoanApplicationAdmin)

class LoanTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'interest_rate', 'loan_duration', 'max_loan_amount')
    search_fields = ('name',)
    list_filter = ('loan_duration',)

admin.site.register(LoanType, LoanTypeAdmin)
