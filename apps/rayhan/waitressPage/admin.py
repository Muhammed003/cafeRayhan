from django.contrib import admin

# Register your models here.
from apps.rayhan.waitressPage.models import *


class WaitressAdmin(admin.ModelAdmin):
    list_display = ['user', 'shift', 'time_started_shift', 'time_ended_shift', 'balance', 'waiter_service']
    list_filter = ['shift']
    ordering = ['-create_date']
    date_hierarchy = "create_date"


class OrderMealAdmin(admin.ModelAdmin):
    list_display = [ 'name','id',"code_bill", 'price','quantity', 'number_of_order', 'people_in_desk', 'create_date', 'comments', 'number_of_desk', 'price', 'price_of_service', 'is_paid', 'order_done', 'author']
    list_filter = ['number_of_order', "code_bill", 'number_of_desk', 'is_paid', 'order_done', 'create_date', 'author', 'price', 'order_done']
    search_fields = ['name', "code_bill"]
    date_hierarchy = "create_date"

class DeletedMealAdmin(admin.ModelAdmin):
    list_display = [ 'name','id',"code_bill", 'price','quantity', 'number_of_order', 'people_in_desk', 'create_date', 'comments', 'number_of_desk', 'price', 'price_of_service', 'is_paid', 'order_done', 'author', 'reason_to_deleting']
    list_filter = ['number_of_order', "code_bill", 'number_of_desk', 'is_paid', 'order_done', 'create_date', 'author', 'price', 'order_done']
    search_fields = ['name', "code_bill"]
    date_hierarchy = "create_date"
class ConsumptionWaitressAdmin(admin.ModelAdmin):
    list_display = ['name', 'create_date', 'user']
    list_filter = ['create_date', 'is_paid']
    ordering = ['-create_date']
    date_hierarchy = "create_date"
    search_fields = ['name', ]


admin.site.register(SettingModel)
admin.site.register(WaitressBank)
admin.site.register(OrderMeal, OrderMealAdmin)
admin.site.register(DeletedMeal, DeletedMealAdmin)
admin.site.register(Waitress, WaitressAdmin)
admin.site.register(ConsumptionWaitress, ConsumptionWaitressAdmin)