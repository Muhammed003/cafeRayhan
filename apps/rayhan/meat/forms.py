from django import forms
from .models import *

class MeatSettingsDefaultForm(forms.ModelForm):
    class Meta:
        model = MeatSettingsDefault
        fields = ['name', 'weight']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
        }



class MeatOrderForm(forms.ModelForm):
    class Meta:
        model = MeatOrder
        fields = ['weight']