from django.forms import ModelForm
from django import forms
from .models import Employee,Permission,Vacation,MonthN as Month
from datetime import date

try:
    active_month = Month.objects.get(active=True)
    if int(active_month.code[5:])==1:
        month_start = date(int(active_month.code[:4])-1,12,16)
    else:
        month_start = date(int(active_month.code[:4]),int(active_month.code[5:])-1,16)
    month_end = date(int(active_month.code[:4]),int(active_month.code[5:]),15)
except Month.DoesNotExist:
    active_month = None
    month_start = None
    month_end = None

class DateInput(forms.DateInput):
    input_type = 'date'

class EmployeeContact(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ('mobile_number','phone_number','emergency_phone','email')

class PermForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = ('date','type','start_time','end_time')
        start_time = forms.TimeInput(format='%H:%M'),
        end_time = forms.TimeInput(format='%H:%M'),
        # exclude = ('date','type')

    date = forms.DateField(widget=DateInput(attrs={'type': 'date', 'min': month_start, 'max': month_end,'class': 'form-control','id':'dateInput','required':""}))

class VacationForm(forms.ModelForm):
    class Meta:
        model = Vacation
        fields = ('date_from','date_to','type', 'photo')
        # exclude = ('date','type')


    date_from = forms.DateField(widget=DateInput(attrs={'type': 'date', 'min': month_start, 'max': month_end,'class': 'form-control','id':'date_from','required':""}))
    date_to = forms.DateField(widget=DateInput(attrs={'type': 'date', 'min': month_start, 'max': month_end,'class': 'form-control','id':'date_to','required':""}))
    # date_to = forms.DateField(widget=DateInput(attrs={'type': 'date', 'min': month_start, 'max': month_end,'class': 'form-control','id':'date_to','required':"",'readOnly':'true'}))
    photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'label': 'مرفق'}))

    # def clean_photo(self):
    #     photo = self.cleaned_data.get('photo')
    #     if photo:
    #         if not photo.content_type.startswith('image'):
    #             raise forms.ValidationError(' وحجم مناسب (jpg, jpeg, png, gif)يرجى التحقق من الصورة. يجب ان تكون احد الامتدادات التالية')
    #     return photo
    
    