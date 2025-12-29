from django.db import models

# Create your models here.



class SettingsKitchen(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Настройка кухни'
        verbose_name_plural = 'Настройка кухня'