from django import forms
from django.contrib.auth.forms import AuthenticationForm

from apps.account.models import CustomUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'input100', "id" : "phone_number", "autocomplete": "new-username",}
        )
        self.fields['password'].widget.attrs.update(
            {'class': 'input100', "id" : "password", "name": "password",  "autocomplete": "new-password",}
        )


    def username_label(self):
        return "Телефон номер"

class ChangePasswordForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Пароль', 'class': 'form-control ', 'name':'password'}), required=True)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Проверка длины пароля
        if len(password) < 8:
            raise forms.ValidationError("Пароль должен быть не менее 8 символов.")

        # Проверка наличия хотя бы одной строчной буквы
        if not any(char.islower() for char in password):
            raise forms.ValidationError("Пароль должен содержать хотя бы одну строчную букву.")

        # Проверка наличия хотя бы одной заглавной буквы
        if not any(char.isupper() for char in password):
            raise forms.ValidationError("Пароль должен содержать хотя бы одну заглавную букву.")

        # Проверка наличия хотя бы одной цифры
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("Пароль должен содержать хотя бы одну цифру.")

        return password



    class Meta:
        model = CustomUser
        fields = ('password', )