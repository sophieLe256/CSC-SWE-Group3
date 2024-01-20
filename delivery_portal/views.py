from django.shortcuts import render
from customer_management.models import Customer
# import customer_management.views as customer_views
from customer_management import views as customer_views

def home(request):
  customers = Customer.objects.all()  
  return render(request, 'home.html', {'customers': customers})

def business_portal(request):
    return redirect('business_portal')