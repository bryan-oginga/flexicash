# loanmanagement/apps.py
from django.apps import AppConfig

class LoanManagementConfig(AppConfig):
    name = 'loanmanagement'

    def ready(self):
        import loanmanagement.signals  # Import the signals module to connect the signal


