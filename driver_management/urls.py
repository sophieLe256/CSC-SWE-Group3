
from django.urls import path
from .views import DriverListView

urlpatterns = [
  path('drivers/', DriverListView.as_view(), name='driver-list'),
]
