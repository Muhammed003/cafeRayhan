from django.contrib.auth.views import LogoutView
from django.urls import path, include
from .views import *

urlpatterns = [
  path("add/user/", AddUserView.as_view(),  name="add-user"),
  path("login/", SignInView.as_view(),  name="login"),
  path('logout/', LogoutView.as_view(), name="logout"),
  path('users/list/', ControlUsersView.as_view(), name="control-users"),
  path('instagram/login/', AccountInstagramView.as_view(), name="account-users"),
  path('users/change/password/<int:pk>/', EditUserView.as_view(), name="password_change"),
  path('not_allowed/', NoPermissionsView.as_view(), name="no_permission_page"),
]