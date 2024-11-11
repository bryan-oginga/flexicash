from loanapplication.models import Transaction
from datetime import datetime, timedelta
from django.utils import timezone


def get_transactions(member, months):
    start_date = datetime.now() - timedelta(days=30 * months)
    return Transaction.objects.filter(member=member, date__gte=start_date).order_by('-date')
