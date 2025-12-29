from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from apps.rayhan.bread.models import WaitressBread, BreadComing


class WaitressBreadForm(forms.ModelForm):
    waitress_bread_type_label = forms.CharField(
        label='Тип хлеба официанта',
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'})
    )

    class Meta:
        model = WaitressBread
        fields = ['quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        waitress_bread_instance = kwargs.get('instance')
        if waitress_bread_instance:
            self.fields['waitress_bread_type_label'].initial = waitress_bread_instance.waitress_bread_type

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'waitress_bread_type_label',
            'quantity',
            Submit('submit', 'Сохранить', css_class='btn btn-primary mx-auto d-block mt-2')  # Add your custom class here
        )


class BreadComingForm(forms.ModelForm):
    bread_type_label = forms.CharField(
        label='Тип хлеба',
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'})
    )

    class Meta:
        model = BreadComing
        fields = ['quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bread_instance = kwargs.get('instance')
        if bread_instance:
            self.fields['bread_type_label'].initial = bread_instance.name

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'bread_type_label',
            'quantity',
            Submit('submit', 'Сохранить', css_class='btn btn-primary mx-auto d-block mt-2')
            # Add your custom class here
        )


