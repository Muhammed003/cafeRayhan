from datetime import datetime

from apps.rayhan.samsa_kebab.models import SamsaPriceDefault, Samsa
from django import forms


class SamsaForm(forms.ModelForm):

    class Meta:
        model = Samsa
        fields = ["samsa_meat", "salary", "samsa_little", "take_away_summa", "for_another_cafe"]


class SamsaDefaultForm(forms.ModelForm):

    class Meta:
        model = SamsaPriceDefault
        exclude = ['author', 'create_date']

    # def save(self, user, samsa_meat_price, samsa_potato_price, samsishnik_meat_pay, samsishnik_potato_pay):
    #     return SamsaPriceDefault.objects.create(author=user,
    #                                               samsa_meat_price=samsa_meat_price,
    #                                               samsa_potato_price=samsa_potato_price,
    #                                               samsishnik_meat_pay=samsishnik_meat_pay,
    #                                               samsishnik_potato_pay=samsishnik_potato_pay,
    #                                               create_date=datetime.now().date())

