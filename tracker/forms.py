from django import forms
from .models import Expense
from django.forms.widgets import DateInput

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'date']
        widgets = {
            'date': DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': 'Select a date'
                },
                format='%Y-%m-%d'  # <-- Important!
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].input_formats = ['%Y-%m-%d']  # <-- Add this too
