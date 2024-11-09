from django.apps import AppConfig

class LoanConfig(AppConfig):
    name = 'loan'

    def ready(self):
        import loan.signals  # Ensure signals are loaded
