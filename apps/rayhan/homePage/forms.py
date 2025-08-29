from django import forms
from django.forms.widgets import TimeInput
from .models import Employee

from django import forms
from django.forms.widgets import TimeInput
from .models import Employee


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'salary', 'image', 'work_start', 'work_end']
        widgets = {
            'work_start': forms.TimeInput(attrs={'type': 'time'}),
            'work_end': forms.TimeInput(attrs={'type': 'time'}),
        }