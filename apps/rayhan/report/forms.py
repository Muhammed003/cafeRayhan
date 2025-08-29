from django import forms
from .models import DeskGroup, DeskAssignment
from ..waitressPage.models import Waitress
from django.utils import timezone

class AssignDesksForm(forms.ModelForm):
    class Meta:
        model = DeskGroup
        fields = ['group_number', 'desks']
        widgets = {
            'desks': forms.TextInput(attrs={'placeholder': 'Пишите номера, и.т.д, 1,2,3'}),
        }


class DeskAssignmentForm(forms.ModelForm):
    class Meta:
        model = DeskAssignment
        fields = ['waitress', 'desk_group', 'shift_date']
        widgets = {
            'shift_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'readonly': 'readonly'}),
            'waitress': forms.Select(attrs={'class': 'form-control'}),
            'desk_group': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(DeskAssignmentForm, self).__init__(*args, **kwargs)

        # Filter waitresses based on today's date (assuming this is your desired logic)
        today = timezone.now().date()
        self.fields['waitress'].queryset = Waitress.objects.filter(create_date=today)

        # Set the shift_date field to today's date and disable editing
        self.fields['shift_date'].initial = today
        self.fields['shift_date'].disabled = True