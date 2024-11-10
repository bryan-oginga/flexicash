from django.contrib import admin
from .models import FlexiCashMember
from decimal import Decimal

@admin.register(FlexiCashMember)
class FlexiCashMemberAdmin(admin.ModelAdmin):
    # Display fields in the list view for quick access
    list_display = (
        'membership_number', 'first_name', 'last_name', 
        'email', 'phone', 'credit_score', 'loan_limit', 'balance'
    )
    
    # Allow search and filtering for faster member lookup
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'membership_number')
    list_filter = ('credit_score', 'loan_limit')
    
    # Display only necessary fields for editing
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'pin')
        }),
        ('Account Details', {
            'fields': ('membership_number', 'balance', 'loan_limit', 'credit_score')
        }),
    )
    
    # Read-only fields for automatic fields
    readonly_fields = ('membership_number',)

    # Custom action to set loan limits based on credit score for selected members
    actions = ['set_loan_limit_based_on_credit_score']

    def set_loan_limit_based_on_credit_score(self, request, queryset):
        updated_count = 0
        for member in queryset:
            initial_loan_limit = member.loan_limit
            member.set_loan_limit_based_on_credit_score()
            if member.loan_limit != initial_loan_limit:
                updated_count += 1
        self.message_user(request, f"Loan limits updated based on credit scores for {updated_count} members.")
    set_loan_limit_based_on_credit_score.short_description = "Update loan limit based on credit score"

