from django.urls import path
from .views import *

urlpatterns = [
    path('list/', ProductListView.as_view(), name='product-list'),
    path('add-to-cart/', AddToCartView.as_view(), name='add-to-cart'),
]
