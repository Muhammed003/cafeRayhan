from django.contrib import admin
from .models import *

class SamsaAdmin(admin.ModelAdmin):
    list_display = ['id', "samsa_meat", "samsa_little", "create_date"]
    ordering = ["-id",]
    date_hierarchy = "create_date"


class SamsaMeatRestAdmin(admin.ModelAdmin):
    list_display = ['id', "samsa_meat_used_to", "samsa_potato_used_to", "create_date"]
    ordering = ["-id",]
    date_hierarchy = "create_date"

admin.site.register(Samsa, SamsaAdmin)
admin.site.register(SamsaMeatRest, SamsaMeatRestAdmin)
admin.site.register(SamsaConsumption)
# admin.site.register(SamsaMeatRest)
admin.site.register(SamsaPriceDefault)
# # Register your models here.
