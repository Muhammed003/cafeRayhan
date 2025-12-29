from django.contrib import admin

from apps.rayhan.kitchen.models import SettingsKitchen

# Register your models here.
class SettingsKitchenAdmin(admin.ModelAdmin):
    list_display = ['name','is_active']
admin.site.register(SettingsKitchen, SettingsKitchenAdmin)