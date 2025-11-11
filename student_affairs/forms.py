from django import forms
from .models import Student,Contact,Application

class ContactData(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['father_mobile', 'mother_mobile', 'phone_number', 'email','address_1']

class ContactContact(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['father_mobile', 'mother_mobile', 'phone_number', 'email','address_1']

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        exclude = ['student','school']
    brother1_grade = forms.ChoiceField(choices=Student.GRADE_CHOICES, widget=forms.Select(attrs={'class': 'form-control form-control-sm'}))
    brother2_grade = forms.ChoiceField(choices=Student.GRADE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    brother3_grade = forms.ChoiceField(choices=Student.GRADE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    brother4_grade = forms.ChoiceField(choices=Student.GRADE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    student_order = forms.ChoiceField(choices=Application.ORDER_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    parents_status = forms.ChoiceField(choices=Application.PARENTS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))