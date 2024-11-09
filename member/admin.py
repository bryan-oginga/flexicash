from django.contrib import admin
from .models import FlexiCashMember, MemberLoan, Transaction

class FlexiCashMemberAdmin(admin.ModelAdmin):
    list_display = ('membership_number', 'first_name', 'last_name', 'email', 'phone', 'balance')
    search_fields = ('membership_number', 'first_name', 'last_name', 'email', 'phone')
    list_filter = ('balance',)

admin.site.register(FlexiCashMember, FlexiCashMemberAdmin)


class MemberLoanAdmin(admin.ModelAdmin):
    list_display = ('loan_type', 'member', 'requested_amount', 'interest_rate', 'loan_balance', 'status', 'due_date')
    list_filter = ('loan_type', 'status', 'member')
    search_fields = ('member__membership_number', 'loan_type__name')

admin.site.register(MemberLoan, MemberLoanAdmin)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'loan', 'amount', 'member', 'date')
    list_filter = ('transaction_type', 'loan__loan_type', 'member')
    search_fields = ('loan__loan_type__name', 'member__membership_number')

admin.site.register(Transaction, TransactionAdmin)
