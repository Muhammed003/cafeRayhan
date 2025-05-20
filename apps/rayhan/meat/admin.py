from django.contrib import admin
from .models import *

class MeatSettingAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'weight',]

class MeatOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'weight', 'create_date', 'create_time_date', 'watched_time']
    ordering = ["-id",]
    date_hierarchy = "create_date"

class MeatOrdersForButcherAdmin(admin.ModelAdmin):
    list_display = ['name', 'weight', 'create_date']
    ordering = ["-id",]
    date_hierarchy = "create_date"
# Register your models here.
admin.site.register(MeatSettingsDefault, MeatSettingAdmin)
admin.site.register(MeatOrder, MeatOrderAdmin)
admin.site.register(MeatPrices)
admin.site.register(MeatOrdersForButcher, MeatOrdersForButcherAdmin)