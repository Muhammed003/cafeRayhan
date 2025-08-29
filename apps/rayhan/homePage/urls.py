from django.urls import path, include
from .views import *

urlpatterns = [
  path("", Main.as_view(),  name="main"),
  path("main/home/", HomePageView.as_view(),  name="home-page"),
  path("settings/list/", SettingsListView.as_view(),  name="settings_list"),
  path("settings/program/", SettingsProgramView.as_view(),  name="settings_program"),

  # path("app-control/", ImportantModelControlView.as_view(), name="app_control"),
  path('filter_model_data/<str:app_label>/<str:model_name>/<str:start_date>/<str:end_date>/', filter_model_data, name='filter_model_data'),
  path('delete_model_data/<str:app_label>/<str:model_name>/<str:start_date>/<str:end_date>/', delete_model_data,
       name='delete_model_data'),
  path("app-control/", AppModelListView.as_view(), name="app_model_list"),
  path('get_model_data/<str:app_label>/<str:model_name>/', get_model_data, name='get_model_data'),
  path('employee/', EmployeeManagementView.as_view(), name='employee-manage'),
  path('not-in-work/', NotInWork.as_view(), name='not_in_work'),
  path('check_bill/', BillCheckPageView.as_view(), name='check_bill_web'),

]