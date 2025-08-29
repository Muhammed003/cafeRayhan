from django import forms
from django.utils import timezone

from .models import MealsInMenu, CommentsInMeal, GroupNameStopList, GroupItemStopList, RatingMeal, ProductPrices, \
    Ingredient


class MealsInMenuForm(forms.ModelForm):
    class Meta:
        model = MealsInMenu
        fields = ['name', 'price', 'group_item', 'type', 'filter_by', 'is_active', 'quantity_of_a_person']


class EditMealsInMenuForm(forms.ModelForm):
    class Meta:
        model = MealsInMenu
        fields = "__all__"


class CommentsInMealForm(forms.ModelForm):
    class Meta:
        model = CommentsInMeal
        fields = ['name']

    name_related_meal = forms.ModelMultipleChoiceField(
        queryset=MealsInMenu.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Тип блюда",
    )


class EditCommentsMealsInMenuForm(forms.ModelForm):
    class Meta:
        model = CommentsInMeal
        fields = "__all__"


class GroupNameStopListForm(forms.ModelForm):
    create_date = forms.DateTimeField(initial=timezone.now, widget=forms.HiddenInput)

    class Meta:
        model = GroupNameStopList
        fields = ["group_name", "create_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group_name'].required = True


class GroupItemStopListForm(forms.ModelForm):
    create_date = forms.DateTimeField(initial=timezone.now, widget=forms.HiddenInput)

    class Meta:
        model = GroupItemStopList
        fields = ["name", "create_date", "name_related_meal"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['name_related_meal'].required = True


class RatingMealForm(forms.ModelForm):
    name_related_meal = forms.ModelChoiceField(queryset=MealsInMenu.objects.order_by("name"),
                                               empty_label="Выберите", label="", required=True, widget=forms.Select(attrs={'class': 'bg-secondary'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantity'].label = ""
        self.initial['quantity'] = ""

    class Meta:
        model = RatingMeal
        fields = ["quantity", "name_related_meal"]

    def save(self, name_related_meal, quantity):
        return RatingMealForm.objects.create(name_related_meal=name_related_meal, quantity=quantity)


class ProductPricesForm(forms.ModelForm):
    class Meta:
        model = ProductPrices
        fields = ["name", "create_date", "price", "type", "type_products"]  # Exclude `create_date` here

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Set the current date if create_date is empty
        if not instance.create_date:
            instance.create_date = timezone.now()
        if commit:
            instance.save()
        return instance



class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'unit', 'source', 'current_price', 'is_available']
