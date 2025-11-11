from django.forms import ModelForm
from django import forms
from .models import Student,BusLocation



class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = ['old_bus', 'living_area','address']

#
class StudentProfile(ModelForm):
    class Meta:
        model = Student
        fields = ['father_mobile', 'mother_mobile', 'phone_number', 'email']
#
class StudentArea(ModelForm):
    def __init__(self, *args, **kwargs):
        super(StudentArea, self).__init__(*args, **kwargs)
        self.fields['living_area'].queryset = BusLocation.objects.filter(school='بنين')
        self.fields['living_area'].empty_label = "اختر اقرب منطقة سكنية"  # This will show as the default empty option
        self.fields['living_area'].label = ""
        self.fields['living_area'].required = True  # Make it required
        self.fields['address'].required = True  # Also make address required if needed

    class Meta:
        model = Student
        fields = ['living_area', 'address']
        widgets = {
            'address': forms.TextInput(attrs={
                'placeholder': 'العنوان',
                'required': 'required'  # HTML5 validation
            }),
        }

class fis_StudentArea(ModelForm):
    def __init__(self, *args, **kwargs):
        super(fis_StudentArea, self).__init__(*args, **kwargs)
        self.fields['living_area'].queryset = BusLocation.objects.filter(school='FIS')
        self.fields['living_area'].empty_label = "Choose the nearest area"  # This will show as the default empty option
        self.fields['living_area'].label = ""
        self.fields['living_area'].required = False  # Make it required
        self.fields['address'].required = True  # Also make address required if needed

    class Meta:
        model = Student
        fields = ['living_area', 'address']
        widgets = {
            'address': forms.TextInput(attrs={
                'placeholder': 'Address',
                'required': 'required'  # HTML5 validation
            }),
        }

class alfarouk_StudentArea(ModelForm):
    def __init__(self, *args, **kwargs):
        super(fis_StudentArea, self).__init__(*args, **kwargs)
        self.fields['living_area'].queryset = BusLocation.objects.filter(school='Alfarouk')
        self.fields['living_area'].empty_label = "Choose the nearest area"  # This will show as the default empty option
        self.fields['living_area'].label = ""
        self.fields['living_area'].required = False  # Make it required
        self.fields['address'].required = True  # Also make address required if needed

    class Meta:
        model = Student
        fields = ['living_area', 'address']
        widgets = {
            'address': forms.TextInput(attrs={
                'placeholder': 'Address',
                'required': 'required'  # HTML5 validation
            }),
        }