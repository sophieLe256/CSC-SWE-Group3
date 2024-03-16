from django.urls import path  
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('', views.business_portal, name='business-portal'),
    # path('business/', views.business_portal, name='business_portal'),
    path('inventory/', views.inventory_view, name='inventory'),
]