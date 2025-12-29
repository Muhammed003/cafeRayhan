import math

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from config import settings


# Create your models here.
class MeatSettingsDefault(models.Model):
    name = models.CharField(max_length=250, verbose_name="Имя блюда", unique=True)
    weight = models.DecimalField(max_digits=10, decimal_places=1, verbose_name="вес")

    class Meta:
        verbose_name = 'Мясо по умолчанию'
        verbose_name_plural = 'Мясы по умолчанию'
        ordering = ['-name']


class MeatOrder(models.Model):
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meat_order')
    name = models.CharField(max_length=100, verbose_name='Имя продукта')
    weight = models.DecimalField(max_digits=10, decimal_places=1, verbose_name="вес")
    create_date = models.DateField(auto_now_add=False, verbose_name="Дата добавления")
    create_time_date = models.DateTimeField(auto_now_add=True, verbose_name="Время добавления")
    is_watched = models.BooleanField(default=False)
    watched_time = models.DateTimeField(auto_now_add=True, verbose_name="Время просмотра")

    class Meta:
        verbose_name = 'Мясо заказ'
        verbose_name_plural = 'Мясо заказы'
        ordering = ['-name']
        unique_together = ['name', 'create_date']

    def clean(self):
        if MeatOrder.objects.filter(name=self.name, create_date=self.create_date).exists():
            raise ValidationError(f'Заказ для "{self.name}" на дату {self.create_date} уже существует.')

    def whenpublished(self):
        now = timezone.now()

        diff = now - self.create_time_date

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds = diff.seconds
            if seconds == 1:
                return str(seconds) + "секунд назад"

            else:
                return str(seconds) + " секунды назад"

        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
            minutes = math.floor(diff.seconds / 60)

            if minutes == 1:
                return str(minutes) + " минута назад"

            else:
                return str(minutes) + " минуты назад"

        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
            hours = math.floor(diff.seconds / 3600)

            if hours == 1:
                return str(hours) + " час назад"

            else:
                return str(hours) + " часы назад"

        # 1 day to 30 days
        if diff.days >= 1 and diff.days < 30:
            days = diff.days

            if days == 1:
                return str(days) + " день назад"

            else:
                return str(days) + " дня назад"

        if diff.days >= 30 and diff.days < 365:
            months = math.floor(diff.days / 30)

            if months == 1:
                return str(months) + " месяц назад"

            else:
                return str(months) + " месяцы назад"

        if diff.days >= 365:
            years = math.floor(diff.days / 365)

            if years == 1:
                return str(years) + " год назад"

            else:
                return str(years) + " годы назад"

    def get_watched_time(self):
        now = timezone.now()

        diff = now - self.watched_time

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds = diff.seconds
            if seconds == 1:
                return str(seconds) + "секунд назад"

            else:
                return str(seconds) + " секунды назад"

        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
            minutes = math.floor(diff.seconds / 60)

            if minutes == 1:
                return str(minutes) + " минута назад"

            else:
                return str(minutes) + " минуты назад"

        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
            hours = math.floor(diff.seconds / 3600)

            if hours == 1:
                return str(hours) + " час назад"

            else:
                return str(hours) + " часы назад"

        # 1 day to 30 days
        if diff.days >= 1 and diff.days < 30:
            days = diff.days

            if days == 1:
                return str(days) + " день назад"

            else:
                return str(days) + " дня назад"

        if diff.days >= 30 and diff.days < 365:
            months = math.floor(diff.days / 30)

            if months == 1:
                return str(months) + " месяц назад"

            else:
                return str(months) + " месяцы назад"

        if diff.days >= 365:
            years = math.floor(diff.days / 365)

            if years == 1:
                return str(years) + " год назад"

            else:
                return str(years) + " годы назад"

    def get_watched_by_butcher(self):
        return self.is_watched


class MeatPrices(models.Model):
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meat_price')
    name = models.CharField(max_length=100, verbose_name='Имя')
    price = models.DecimalField(max_digits=10, decimal_places=1, verbose_name="цена")
    create_date = models.DateField(auto_now_add=False, verbose_name="Дата добавления")

    def __str__(self):
        return f"{self.name}  ---------   {self.price}"

    class Meta:
        verbose_name = 'Мясо цена'
        verbose_name_plural = 'Мясо цены'
        ordering = ['-name']

class MeatOrdersForButcher(models.Model):
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meat_for_butcher')
    name = models.CharField(max_length=100, verbose_name='Имя')
    weight = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Вес")
    summa = models.IntegerField(verbose_name="Сумма")
    create_date = models.DateField(auto_now_add=False, verbose_name="Дата добавления")
    is_paid = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Мясо мясника"
        verbose_name_plural = "Мясы мясника"

    def __str__(self):
        return f"{self.name} -----{self.create_date}"

