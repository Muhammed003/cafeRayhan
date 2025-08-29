from django.urls import path, include
from .views import *

urlpatterns = [
  # ORDER BILL SIDE
  path('shift-waitress/', WantToStartShift.as_view(), name='shift-waitress'),
  path('shift-waitress/confirm/<int:pk>/', ConfirmShiftStart.as_view(), name='confirm-shift-to-start'),
  path('orders/', OrdersInKitchenView.as_view(), name='orders-in-kitchen'),
  path('uyghur/orders/', UyghurKitchenView.as_view(), name='uyghur-kitchen'),
  path('national/orders/', NationalKitchenView.as_view(), name='national-kitchen'),

  path('cakes/', OrderCakesView.as_view(), name='cakes-order'),

  path('control/orders/', ControlKitchenOrders.as_view(), name='control-orders-in-kitchen'),


  path('delete/orders/', DeleteOrderView.as_view(), name='delete_order'),
  path('deleted_orders/list/', ControlDeletedOrderView.as_view(), name='list_of_deleted_orders'),
  path('deleted_orders/list/recovery/<int:pk>/', RecoveryDeletedMealView.as_view(), name='recovery_deleted_order'),


  path('orders/<int:number_of_desk>/<str:params>/', orderDoneGroup, name='order-done-group'),

  path('orders/by_one/<int:id>/<str:params>/', orderDoneByOne, name='order-done-by-one'),
  path('sos_message/', sosMessage, name='sos-message'),


  # ORDER TEA
  path('tea/orders/', OrdersTea.as_view(), name='tea-order'),

  path('list_of_names/', ListOfNominationOrderView.as_view(), name='list-of-nomination'),
  path('bills_kitchen/', BillsAllKitchen.as_view(), name='bills-all-kitchen'),
  path('bills_detail_kitchen/<int:pk>/<int:number_of_order>/<str:code_bill>/<str:history>/', BillsDetailAllKitchen.as_view(), name='kitchen-bill-detail'),

]
