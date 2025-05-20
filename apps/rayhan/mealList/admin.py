from django.contrib import admin

# Register your models here.
from apps.rayhan.mealList.models import *


class GroupItemStopListAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_related_meal']
    list_filter = ['name', ]

class MealRecipesAdmin(admin.ModelAdmin):
    list_display = ['meal', 'name_product', 'weight']
    list_filter = ['meal', ]

class ProductPricesAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'type']
    list_filter = ['price','name', 'create_date' ]


class RatingMealAdmin(admin.ModelAdmin):
    list_display = ['name_related_meal', 'quantity', 'create_date']
    list_filter = ['create_date', ]
    date_hierarchy = "create_date"



class CommentsInMealAdmin(admin.ModelAdmin):
    list_display = ['name_related_meal', 'name']
    list_filter = ['name_related_meal', ]

class MealsInMenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['group_item', ]
    ordering = ['name', ]

class StopListAdmin(admin.ModelAdmin):
    list_display = ['name', 'time_create_date']
    list_filter = ['name', ]
    ordering = ['-create_date']
    date_hierarchy = "create_date"


admin.site.register(MealsInMenu, MealsInMenuAdmin)
admin.site.register(MealsToShow)
admin.site.register(Drinks)
admin.site.register(BlackListToKitchen)
admin.site.register(GroupNameStopList)
admin.site.register(MealGroup)
admin.site.register(ContainerType)
admin.site.register(GroupByOther)
admin.site.register(CommentsInMeal, CommentsInMealAdmin)

admin.site.register(RatingMeal, RatingMealAdmin)

admin.site.register(StopList, StopListAdmin)
admin.site.register(MealRecipes, MealRecipesAdmin)
admin.site.register(ProductPrices, ProductPricesAdmin)
admin.site.register(GroupItemStopList, GroupItemStopListAdmin)
admin.site.register(InStockInMeal, RatingMealAdmin)