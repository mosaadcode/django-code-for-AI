from django.forms import ModelForm
from django import forms
from .models import Fee

class DateInput(forms.DateInput):
    input_type = 'date'

class FeesForm(ModelForm):
    class Meta:
        model = Fee
        # fields = ['year' ,'kind', 'payment_date', 'bank_account','value']
        fields = ['kind', 'payment_date', 'bank_account','value']
    payment_date = forms.DateField(widget=DateInput)
