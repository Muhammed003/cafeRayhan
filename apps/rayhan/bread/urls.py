from django.urls import path, include
from .views import *

urlpatterns = [
  path("", BreadPage.as_view(),  name="bread-page"),
  path("page_delete/", EditBreadComingView.as_view(),  name="bread-coming-delete"),
  path('edit/<int:pk>/', EditBreadComingView.as_view(), name='edit-bread-coming'),
  path('delete/<int:pk>/', WaitressBreadDeleteView.as_view(), name='delete-bread-coming'),

  path('main_bread/edit/<int:pk>/', EditBreadMainPageView.as_view(), name='edit-main-of-bread'),
  path('main_bread/delete/<int:pk>/', DeleteBreadMainPageView.as_view(), name='delete-main-of-bread'),
]
