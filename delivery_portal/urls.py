from django.contrib import admin
from django.urls import path, include
from . import views
from customer_management import views as customer_views  # Correct import statement

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('drivers/', include('driver_management.urls')),
    path('customers/', include('customer_management.urls')),
    path('customers/portal/', customer_views.customer_portal, name='customer_portal'),
    path('business/', views.business_portal, name='business_portal'),
]
