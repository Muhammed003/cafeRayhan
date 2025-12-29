from django.urls import path, include
from .views import *

urlpatterns = [
  # ORDER BILL SIDE
  path('main/', GameStartView.as_view(), name='game-start-view'),

]
