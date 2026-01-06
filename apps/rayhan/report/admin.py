from django.contrib import admin

from apps.rayhan.report.models import DeskGroup, DeskAssignment, SaveEveryDaysReport, CountMeals, BakeryDailyReport


class DeskGroupAdmin(admin.ModelAdmin):
    list_display = ['group_number', 'desks']
    list_filter = ['group_number',]


class DeskAssignmentAdmin(admin.ModelAdmin):
    list_display = ['waitress', 'desk_group', 'shift_date']
    list_filter = ['shift_date']

class CountMealsAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'create_date']
    list_filter = ['create_date']
    date_hierarchy = 'create_date'
    search_fields = ['name', ]

# Register your models here.
admin.site.register(DeskGroup, DeskGroupAdmin)
admin.site.register(DeskAssignment, DeskAssignmentAdmin)
admin.site.register(SaveEveryDaysReport)
admin.site.register(CountMeals, CountMealsAdmin)
admin.site.register(BakeryDailyReport)