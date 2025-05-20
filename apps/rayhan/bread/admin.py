from django.contrib import admin

# Register your models here.
from apps.rayhan.bread.models import BreadComing, WaitressBread


class BreadComingAdmin(admin.ModelAdmin):
    list_display = ['user', 'name','quantity', 'create_date']
    list_filter = ['create_date']
    search_fields = ['user']
    date_hierarchy = "create_date"


class WaitressBreadAdmin(admin.ModelAdmin):
    list_display = ['author', 'waitress_bread_type','quantity', 'create_date']
    list_filter = ['create_date']
    search_fields = ['waitress_bread_type']
    date_hierarchy = "create_date"


admin.site.register(BreadComing, BreadComingAdmin)
admin.site.register(WaitressBread, WaitressBreadAdmin)