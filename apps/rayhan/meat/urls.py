from django.urls import path
from .views import *

urlpatterns = [
    path('meat-settings/', meat_settings_view, name='meat_settings'),
    path('order/', MeatOrderPageView.as_view(), name='meat_order'),
    path('order/edit/', EditOrderMeatView.as_view(), name='edit_meat_view'),

    path('butcher/', ButcherMainView.as_view(), name='butcher-main'),
    path('butcher/orders/', ButcherMeatOrdersView.as_view(), name='butcher-meat-orders'),
    path('history/orders/', HistoryButcherMeatOrdersView.as_view(), name='butcher-meat-orders-history'),
    path('history/unpaid/orders/', UnPaidMeatOrdersView.as_view(), name='unpaid-meat-orders'),
    path('pay-orders/<str:pk>/', meat_is_paid, name='pay-orders'),
]
