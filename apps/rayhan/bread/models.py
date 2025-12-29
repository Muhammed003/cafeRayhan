from datetime import datetime

from django.db import models

# Create your models here.
from apps.rayhan.waitressPage.models import Waitress
from config import settings


class BreadComing(models.Model):
    BREAD_TYPES = (
        ("Шеф", "Шеф"),
        ("Пекар", "Пекар"),
    )
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bread_coming')
    name = models.CharField(choices=BREAD_TYPES, max_length=255, default="first_meal", verbose_name='Человек которые принес')
    quantity = models.DecimalField(decimal_places=1, max_digits=12, verbose_name='Количества')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления", null=True, blank=True)

    class Meta:
        verbose_name = 'Лепешка'
        verbose_name_plural = 'Лепешки'


class WaitressBread(models.Model):
    author = models.ForeignKey(to=Waitress, on_delete=models.PROTECT, related_name='bread_waitress')
    waitress_bread_type = models.ForeignKey(to=Waitress, on_delete=models.CASCADE, related_name='bread_waitress_type')
    quantity = models.DecimalField(decimal_places=1, max_digits=12, verbose_name='Количества')
    create_date = models.DateField(auto_now_add=True, verbose_name="Дата добавления", null=True, blank=True)

    def __str__(self):
        return self.waitress_bread_type.user.username

    class Meta:
        verbose_name = 'Лепешка официанта'
        verbose_name_plural = 'Лепешки официанты'

    @property
    def get_absolute_user(self):
        return self.waitress_bread_type.user.id

    @property
    def get_sum_bread(self):
        waitress_bread = WaitressBread.objects.filter(create_date=datetime.now().date(), waitress_bread_type=self.waitress_bread_type)
        bread = sum([x.quantity for x in waitress_bread])
        return bread
