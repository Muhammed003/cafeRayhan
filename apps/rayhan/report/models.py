from django.db import models

from apps.rayhan.waitressPage.models import Waitress

from django.utils import timezone

from config import settings


# Create your models here.
class DeskGroup(models.Model):
    group_number = models.PositiveSmallIntegerField(verbose_name='Номер группы', unique=True)
    desks = models.CharField(max_length=255, verbose_name='Номера столов', unique=True)  # Store desks as comma-separated values

    class Meta:
        verbose_name = 'Группа столов'
        verbose_name_plural = 'Группы столов'
        ordering = ['group_number']

    def __str__(self):
        return f"Группа {self.group_number} эти: {self.desks}"


class DeskAssignment(models.Model):
    waitress = models.ForeignKey(Waitress, on_delete=models.CASCADE, related_name='desk_assignments', verbose_name='Официантка')
    desk_group = models.ForeignKey(DeskGroup, verbose_name='Группа столов', on_delete=models.CASCADE)
    shift_date = models.DateField(default=timezone.now, verbose_name='Дата смены')

    class Meta:
        verbose_name = 'Назначение столов'
        verbose_name_plural = 'Назначения столов'
        ordering = ['shift_date', 'desk_group']
        constraints = [
            models.UniqueConstraint(fields=['waitress', 'shift_date', 'desk_group'], name='unique_assignment')
        ]

    def __str__(self):
        return f"{self.waitress} - Group {self.desk_group} on {self.shift_date}"


class SaveEveryDaysReport(models.Model):
    all_balance = models.PositiveIntegerField(default=0, verbose_name='Сумма')
    kitchen = models.PositiveIntegerField(default=0, verbose_name='Кухня')
    samsa = models.PositiveIntegerField(default=0, verbose_name='Самса')
    kebab = models.PositiveIntegerField(default=0, verbose_name='Шашлыки')
    create_date = models.DateTimeField(auto_now_add=False, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Сохранение отчета"
        verbose_name_plural = "Сохранение отчеты"

    def __str__(self):
        return f"{self.create_date.strftime('%d-%m-%Y')}"


class CountMeals(models.Model):
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='count_meals')
    name = models.CharField(max_length=300, verbose_name='Имя', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количества')
    create_date = models.DateTimeField(auto_now_add=False, verbose_name="Дата")
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Блюд штук"
        verbose_name_plural = "Блюды штук"

    def __str__(self):
        return f"{self.name} ----{self.create_date.strftime('%d-%m-%Y')}"
