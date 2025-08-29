from django.urls import path
from .views import *

urlpatterns = [
    path('kebab/', OrdersSamsaKebabView.as_view(), name='samsa_kebab'),
    path('order_samsa/', OrdersSamsaView.as_view(), name='order_samsa'),
    path('order_kebab/', OrdersKebabView.as_view(), name='order_kebab'),
    path('history_samsa_kebab/', ControlSamsaKebabOrders.as_view(), name='samsa_kebab_history'),
    path('samsa_report/', SamsaReportAddView.as_view(), name='samsa_report_add'),
    path('samsa_settings/', SamsaSettingsView.as_view(), name='samsa_settings'),
    path('samsa_edit/', EditSamsaConsumption.as_view(), name='samsa-edit-consumption'),
    path('delete/<int:pk>/', SamsaSettingsDeleteView.as_view(), name='samsa_settings_delete'),
    path('rest_meat/', SamsaRestReportView.as_view(), name='samsa_rest_meat'),
    path('rest_meat/<str:pk>/', SamsaRestReportDetailView.as_view(), name='samsa_rest_meat_detail'),
]
