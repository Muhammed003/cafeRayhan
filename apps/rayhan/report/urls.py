from django.urls import path, include
from .views import *

urlpatterns = [
    path("notebook/", ReportNoteBook.as_view(), name="note-book"),
    path('history/', HistoryReportView.as_view(), name='report-history'),
    path('history/detail/<str:pk>/', HistoryDetailReportView.as_view(), name='report-history-detail'),


    path("z_report/", ZReportView.as_view(), name="z-report"),
    path("analytics/", AnalyticsReportView.as_view(), name="analytics-report"),
    path("analytics/shift/", ShiftAnalyticsView.as_view(), name="shift-analytics"),
    path('api/meal-hourly-quantity/', MealHourlyQuantityAPIView.as_view(), name='meal-hourly-quantity-api'),
    path("z_report  /detail/<str:pk>/", ZReportDetailView.as_view(), name="z-report-detail"),
    path("request_to_close_shift/", RequestToCloseShiftWaitress.as_view(), name="request-close-shift"),
    path("request_to_close_shift/detail/<int:pk>/", RequestShiftDetailView.as_view(), name="request-close-shift-detail"),
    path("request_to_close_shift/end_shift/<int:pk>/", EndRequestShiftDetailView.as_view(), name="end-shift-waitress"),

    path("debts/waitress/by_month/", DebtsWaitressByMonth.as_view(), name="debts-waitress-by-month"),
    path('debts/waitress/month/detail/<str:pk>/', DebtsByMonthDetailView.as_view(), name='debts_by_month_detail'),
    path('debts/waitress/month/pay/<int:pk>/', DebtPaidByMonth.as_view(), name='debts-paid-by-month'),
    path('distribute/desks/', AssignDesksView.as_view(), name='divide_desks'),

    path('desk/assignments/', DeskAssignmentListView.as_view(), name='desk-assignment-list'),
    path('desk/assignments/new/', DeskAssignmentCreateView.as_view(), name='desk-assignment-create'),
    path('sale_day/', SaleDayView.as_view(), name='sale-day'),
    path('sale_month/', SaleMonthView.as_view(), name='sale-month'),
    path('bill_is_paid/', HistoryBillIsPaidView.as_view(), name='bill_is_paid'),
    path('not_ended_report/', NotEndedReportView.as_view(), name='not_ended_report'),
    path('not_ended_report/close/<str:pk>/', CloseNotEndedReports.as_view(), name='close-not-ended-reports'),
    path('by_hour/', ReportByHourView.as_view(), name='report_by_hour'),
    path('tax_auto/',  TaxAutoDataView.as_view(),  name='tax-auto'),
    path('income/',  InComeView.as_view(),  name='income-report'),
    path('time_cooked/',  TimeCookedView.as_view(),  name='time-cooked'),

    path('cakes_report/', BakeryReportSingleView.as_view(), name='bakery-report-single'),
    path('yesterday/',  ReportYesterdayView.as_view(),  name='report-yesterday'),

    path('waitress/control_crud/',  WaitressControlCrudReport.as_view(),  name='waitress_crud'),
    path('waitress/price_of_service/',  WaitressPriceOfServiceMonthlyView.as_view(),  name='waitress-service'),
    path('bread/year/',  BreadYearView.as_view(),  name='bread-month'),


]