
from django import forms
from .models import TransactionHistory

class TransactionHistoryForm(forms.ModelForm):
    class Meta:
        model = TransactionHistory
        fields = ['user', 'transaction_type', 'balance_after_transaction']


