from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('portal/', views.customer_portal, name='customer_portal'),
]
