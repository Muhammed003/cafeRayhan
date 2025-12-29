from django.urls import path, include
from .views import *

urlpatterns = [
  path("list/", MealListView.as_view(),  name="meal-list"),
  path("list/search/", MealSearchView.as_view(),  name="meal-search"),
  path("add/", AddMealView.as_view(),  name="add-meal"),
  path("edit/<int:pk>/", EditMealsView.as_view(),  name="edit-meal"),
  path("comments/add/", CommentsInMealView.as_view(),  name="add-comments-meal"),
  path("comments/edit/<int:pk>/", EditCommentsMealsInMenu.as_view(),  name="edit-comments-meal"),
  path("comments/edit/<int:pk>/", EditCommentsMealsInMenu.as_view(),  name="edit-comments-meal"),
  path("stop/list/", StopListView.as_view(),  name="stop-list"),
  path("group/stop/list/", GroupStopListView.as_view(),  name="group-stop-list"),
  path("group/add/group_name/", AddGroupNameToStopListView.as_view(),  name="add-group-stop-list"),
  path("group/add/item_name/", AddGroupItemToStopListView.as_view(),  name="add-item-stop-list"),

  #MENU IN SCREEN
  path("menu/", MenuView.as_view(),  name="menu"),
  # QUANTITY OF MEAL A DAY
  path("quantity/", QuantityOfMealADay.as_view(),  name="quantity-of-meal"),
  path("average_quantity/", AverageQuantityMeals.as_view(),  name="quantity-of-meal"),
  # RATING MEAL
  path("rating/", RatingMealView.as_view(),  name="rating-meal"),
  path("in_stock/", MealInStockView.as_view(),  name="meal-in-stock"),

  # REPORT MEAL
  path("report/list/", MealReportList.as_view(), name="meal-report-list"),
  path("report/product/price/", ProductPriceView.as_view(), name="product-price"),
  path("report/meal-recipes/",  MealRecipesView.as_view(), name='meal-recipes'),
  path("cakes/quantity/",  QuantityOfCakesView.as_view(), name='quantity_of_cakes'),
  path("history/quantity_meals/",  HistoryQuantityOfMealsView.as_view(), name='history_quantity_meals'),

  # NEW REPORT MEALS CONTROL
  path('ingredients/', IngredientView.as_view(), name='ingredient-list'),
  path('meal-ingredient/', MealIngredientView.as_view(), name='meal-ingredient'),
  path('product-purchase/', ProductPurchaseView.as_view(), name='product-purchase'),
  path('ingredient/stock-report/', IngredientStockView.as_view(), name='ingredient-stock-report'),

]