from django.contrib import admin
from django.utils import timezone
from .models import LoanType, LoanApplication

# Customizing LoanType admin
class LoanTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'interest_rate', 'loan_duration', 'max_loan_amount', 'description')
    list_filter = ('loan_duration',)
    readonly_fields = ('interest_rate',)
    search_fields = ('name',)
    ordering = ['loan_duration', 'name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'interest_rate', 'loan_duration', 'max_loan_amount', 'description')
        }),
    )

# Customizing LoanApplication admin
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'member', 'loan_type', 'amount_requested', 'application_status', 'interest_rate', 'loan_due_date', 'payment_complete', 'application_date')
    list_filter = ('application_status', 'loan_type', 'payment_complete', 'loan_due_date')
    search_fields = ('loan_id', 'member__phone_number', 'member__email', 'loan_type__name')
    readonly_fields = ('interest_rate',)
    
    # Exclude application_date and some other fields from being displayed in the form
    exclude = ('application_date',)  # Or simply remove this line to include application_date

    actions = ['approve_loan', 'reject_loan']
    
    def approve_loan(self, request, queryset):
        updated = queryset.update(application_status='APPROVED', approval_date=timezone.now())
        self.message_user(request, f'{updated} loan applications were successfully approved.')
    approve_loan.short_description = "Approve selected loan applications"
    
    def reject_loan(self, request, queryset):
        updated = queryset.update(application_status='REJECTED', rejection_date=timezone.now())
        self.message_user(request, f'{updated} loan applications were successfully rejected.')
    reject_loan.short_description = "Reject selected loan applications"

    # Explicitly including fields in the form
    fieldsets = (
        (None, {
            'fields': (
                'loan_id', 'member', 'loan_type', 'amount_requested', 'application_status', 
                'interest_rate', 'interest_amount', 'total_repayment', 'profit', 'approval_date', 
                'rejection_date', 'comments', 'payment_complete', 'loan_due_date', 'loan_duration'
            )
        }),
    )

# Register models with custom admin interfaces
admin.site.register(LoanType, LoanTypeAdmin)
admin.site.register(LoanApplication, LoanApplicationAdmin)
