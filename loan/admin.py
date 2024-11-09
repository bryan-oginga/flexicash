from django.contrib import admin
from .models import LoanApplication, LoanType

class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'interest_rate', 'loan_type', 'amount_requested', 'loan_status', 'payment_complete')
    readonly_fields = ('interest_rate',)

    def loan_id(self, obj):
        return obj.loan_id  # Use the primary key for loan ID
    loan_id.short_description = 'Loan ID'

    def interest_rate(self, obj):
        return obj.loan_type.interest_rate  # Fetch the interest rate from the related LoanType
    interest_rate.short_description = 'Interest Rate'

    def payment_complete(self, obj):
        return "Yes" if obj.loan_balance == 0 else "No"
    payment_complete.short_description = 'Payment Complete'

    list_filter = ('loan_status', 'loan_type')

admin.site.register(LoanApplication, LoanApplicationAdmin)
admin.site.register(LoanType)
