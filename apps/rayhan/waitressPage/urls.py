from django.urls import path, include
from .views import *

urlpatterns = [
  # WAITRESS SIDE
  path("", WaitressPageView.as_view(),  name="waitress-page"),
  path('start/work/', StartShiftWaitress.as_view(), name='start-work'),
  path('start/late_user_work/<int:price>/', StartLateUserShiftWaitress.as_view(), name='late-user-start-work'),
  path('end/work/', EndShiftWaitress.as_view(), name='end-work'),
  # END WAITRESS SIDE

  # ORDER DESK SIDE
  path("desks/", DesksView.as_view(),  name="desks"),
  path("desks_simple/", DesksSimpleView.as_view(),  name="desks_simple"),
  path("desks/edit/order/<int:pk>/", EditOrderWaitress.as_view(),  name="edit-order-waitress"),
  path('desks/new/order/', NewOrderView.as_view(), name='new-order-meal'),
  path('kitchen/', AllWaitressView.as_view(), name='waitress-kitchen'),
  path('orders_kitchen_waitress/<str:pk>/', KitchenWaitressView.as_view(), name='orders_waitress_kitchen'),
  # END DESK SIDE

  # ORDER TAKEAWAY SIDE
  path('take-away/', TakeAwayFoodView.as_view(), name='take-away-page'),
  path('take-away/new-order/', NewOrderTakeAwayFood.as_view(), name='order-takeaway'),
  path('take-away/bill/<int:number_of_order>/<str:code_bill>/', BillTakeAwayFoodView.as_view(), name='bill-takeaway'),
  path('take-away/edit/<int:pk>/<int:code_bill>/', EditOrderWaitressTakeAwayView.as_view(), name='edit-order-takeaway'),
  # END ORDER TAKEAWAY SIDE

  # ORDER BILL SIDE
  path('bill/<str:type_bill>/', BillWaitressView.as_view(), name='order-bill'),
  path('bill/<int:pk>/<int:number_of_order>/<str:code_bill>/<str:history>/', BillWaitressDetailView.as_view(), name='order-bill'
                                                                                                      '-detail'),
  path('bill/detail/end-order/<int:pk>/<int:number_of_order>/<str:code_bill>/<str:cash>/', EndOrder.as_view(), name='close_order'),
  # END ORDER BILL SIDE

  # CONSUMPTIONS SIDE
  path('consumptions/', ConsumptionsWaitressView.as_view(), name='consumptions-waitress'),
  path('consumptions/history/', ConsumptionsWaitressHistoryView.as_view(), name='consumptions-history'),
  # END CONSUMPTIONS SIDE


  # PROFILE VIEW
  path('profile/', ProfilePageView.as_view(), name='profile-page'),
  # LIST OF PROGRAMS VIEW
  path('programs/', ListOfProgramsView.as_view(), name='programs-page'),
  path('balance_in_card/', BalanceFromCardView.as_view(), name='balance-card'),
  path('waitress_list_items/', ListOfItemsWaitressView.as_view(), name='waitress-list-items'),
  path('rate_waitress/', RateWaitressView.as_view(), name='rate-waitress'),
  path('rules_waitress/', RulesWaitressView.as_view(), name='rules-waitress'),
  path('pay_with_qr_code/', PayWithQr.as_view(), name='pay_with_qr_code'),
  path('qr_code_input/', QrCodeInput.as_view(), name='qr_code_input'),

  path('save-subscription/', save_subscription, name='save_subscription'),
  path('vapid-public-key/', vapid_public_key, name='vapid_public_key'),
  path('menu_order/<int:table_id>/', MenuOrderClientView.as_view(), name='new-order-client'),
  path('client/order/<int:table_id>/', client_order, name='client-order'),
  path('client/order/delete/<int:order_id>/', DeleteClientOrderView.as_view(), name='client-order-delete'),
  path('order_client_student/', WaitressClientOrdersView.as_view(), name='client_order_student'),
  path('confirm_order/<int:order_id>/', confirm_order, name='confirm-order-student'),

]
