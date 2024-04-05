
from .views import business_portal, home, inventory_view, update_package_status, create_shipment
from django.urls import path
from . import views

app_name = 'business'

urlpatterns = [
    path('portal/', views.business_portal, name='business-portal'),
    path('create-shipment/', views.create_shipment, name='create-shipment'),
    path('inventory/', views.inventory_view, name='inventory'),
    path('add-driver/', views.add_driver, name='add-driver'),
    path('update-package-status/<int:package_id>/', views.update_package_status, name='update-package-status'),
    path('update-order-status/<int:order_id>/', views.update_order_status, name='update-order-status'),
]
