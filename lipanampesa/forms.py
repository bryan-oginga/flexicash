from django import forms

class PaymentForm(forms.Form):
    phone_number = forms.CharField(max_length=15, required=True, help_text="Enter your phone number")
    amount = forms.DecimalField(max_digits=10, decimal_places=2, required=True, help_text="Enter the amount to pay")
    narrative = forms.CharField(max_length=255, required=True, help_text="Enter the payment description")
