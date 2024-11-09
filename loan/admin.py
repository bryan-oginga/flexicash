from django.contrib import admin
from .models import LoanApplication, LoanType

class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'interest_rate', 'loan_type', 'amount_requested', 'loan_status', 'payment_complete')
    readonly_fields = ('interest_rate',)

    def loan_id(self, obj):
        return obj.loan_id  # Use the primary key for loan ID

    def interest_rate(self, obj):
        return obj.loan_type.interest_rate  # Fetch the interest rate from the related LoanType

    def payment_complete(self, obj):
        return "Yes" if obj.loan_balance == 0 else "No"

    list_filter = ('loan_status', 'loan_type')

admin.site.register(LoanApplication, LoanApplicationAdmin)
