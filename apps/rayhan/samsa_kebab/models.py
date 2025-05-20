from django.db import models

from apps.rayhan.mealList.models import MealsInMenu
from config import settings


# Create your models here.
class Samsa(models.Model):

    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='samsa')
    samsa_meat = models.PositiveIntegerField(verbose_name='Мясная самса')
    samsa_potato = models.PositiveIntegerField(verbose_name='Самса картофельная')
    salary = models.PositiveIntegerField(default=0, verbose_name='Зарплата')
    create_date = models.DateField(auto_now_add=False, unique=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Самса'
        verbose_name_plural = 'Самсы'

    @property
    def sum_of_samsa_meat(self):
        samsa_meat_data = MealsInMenu.objects.get(name="Самса")
        return self.samsa_meat * samsa_meat_data.price

    @property
    def sum_of_samsa_potato(self):
        samsa_potato_data = MealsInMenu.objects.get(name="Самса картошка")
        return self.samsa_potato * samsa_potato_data.price


class SamsaPriceDefault(models.Model):

    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='samsa_price')
    samsa_meat_price = models.CharField(max_length=100, verbose_name='Мясная самса')
    samsa_potato_price = models.CharField(max_length=100, verbose_name='Самса картофельная')
    samsishnik_meat_pay = models.CharField(max_length=100, verbose_name='Зарплата шт мясная самса')
    samsishnik_potato_pay = models.CharField(max_length=100, verbose_name='Зарплата шт картофельная самса')
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Самса цена зарплата'
        verbose_name_plural = 'Самсы цены зарплаты'


class SamsaConsumption(models.Model):
    TYPE_SAMSA = (
        ("картошка", "картошка"),
        ("мясная", "мясная"),
    )
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='samsa_consumption')
    name = models.CharField(max_length=100, verbose_name='Имя')
    quantity = models.CharField(max_length=100, verbose_name='Количества')
    type_samsa = models.CharField(choices=TYPE_SAMSA, max_length=255, default="картошка", verbose_name='Тип')
    create_date = models.DateTimeField(auto_now_add=False)
    update_date = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = 'Самса расход'
        verbose_name_plural = 'Самса расходы'

    @property
    def sum_of_samsa_consumption(self):
        samsa_meat_data = MealsInMenu.objects.get(name="Самса")
        samsa_potato_data = MealsInMenu.objects.get(name="Самса картошка")
        result = []
        if self.type_samsa == "картошка":
            result.append(samsa_potato_data.price * int(self.quantity))
        elif self.type_samsa == "мясная":
            result.append(samsa_meat_data.price * int(self.quantity))
        return sum(result)


class SamsaMeatRest(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')
    samsa_meat_used_to = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Мясной самса', null=True)
    samsa_potato_used_to = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Картошка самса', null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="вес", null=True)
    create_date = models.DateField(auto_now_add=False)

    class Meta:
        verbose_name = 'Самса остатка'
        verbose_name_plural = 'Самса остатки'
