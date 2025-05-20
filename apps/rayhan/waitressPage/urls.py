from django.urls import path, include
from .views import *

urlpatterns = [
  # WAITRESS SIDE
  path("", WaitressPageView.as_view(),  name="waitress-page"),
  path('start/late_user_work/<int:price>/', StartLateUserShiftWaitress.as_view(), name='late-user-start-work'),
  path('start/work/', StartShiftWaitress.as_view(), name='start-work'),
  path('end/work/', EndShiftWaitress.as_view(), name='end-work'),
  # END WAITRESS SIDE

  # ORDER DESK SIDE
  path("desks/", DesksView.as_view(),  name="desks"),
  path("desks_simple/", DesksSimpleView.as_view(),  name="desks_simple"),
  path("desks/edit/order/<int:pk>/", EditOrderWaitress.as_view(),  name="edit-order-waitress"),
  path('desks/new/order/', NewOrderView.as_view(), name='new-order-meal'),
  path('kitchen/', KitchenWaitressView.as_view(), name='waitress-kitchen'),
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



]
