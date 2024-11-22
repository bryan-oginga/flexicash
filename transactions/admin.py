from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_id",
        "member",
        "loan",
        "amount",
        "transaction_type",
        "state",
        "repayment_type",
        "date",
    )  # Fields to display in the admin list view
    
    list_filter = (
        "transaction_type",
        "repayment_type",
        "state",
        "date",
    )  # Filters in the sidebar

    search_fields = (
        "invoice_id",
        "phone_number",
        "member__name",  # Assuming the FlexiCashMember model has a 'name' field
        "loan__application_ref",  # Assuming the MemberLoanApplication model has 'application_ref'
    )  # Fields for the search bar

    ordering = ("-date",)  # Default ordering in the admin list view


    date_hierarchy = "date"  # Adds a date-based drill-down navigation

    readonly_fields = ("invoice_id", "date", "state",)  # Fields that should be non-editable

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("invoice_id", "member", "loan", "transaction_type", "repayment_type", "amount", "narrative"),
            },
        ),
        (
            "Customer Details",
            {
                "fields": ("phone_number", "email"),
            },
        ),
        (
            "Status",
            {
                "fields": ("state", "date"),
            },
        ),
    )  # Organizing fields into collapsible sections for better usability
