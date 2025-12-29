from django.db import models
from datetime import datetime
# Create your models here.
def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Employee(models.Model):
    name = models.CharField(max_length=252, verbose_name='Имя', blank=True, null=True, unique=True)
    salary = models.PositiveIntegerField(default=0, verbose_name='Зарплата')
    image = models.ImageField(upload_to='cooks', verbose_name='Фото', blank=True, null=True)
    work_start = models.TimeField(default=get_now, verbose_name='Время работы от')
    work_end =  models.TimeField(default=get_now, verbose_name='Время работы до')

    class Meta:
        verbose_name = "Наёмник"
        verbose_name_plural = "Наёмники"

    def __str__(self):
        return self.name