from django.urls import path
from . import views
from .views import business_portal, home, inventory_view, update_package_status, create_shipment

app_name = 'business'

urlpatterns = [
    path('', home, name='home'),
    path('portal/', views.business_portal, name='business-portal'),
    path('inventory/', inventory_view, name='inventory'),
    path('create-shipment/', create_shipment, name='create-shipment'),
    path('update-package-status/<int:package_id>/', views.update_package_status, name='update-package-status'),
]
