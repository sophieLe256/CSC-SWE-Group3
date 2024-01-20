from django.shortcuts import render, redirect

def home(request):

  if request.GET.get('customer'): 
    return redirect('customer_portal')
  if request.GET.get('business'):
    return redirect('business_portal')

  return render(request, 'home.html')


def customer_portal(request):
  return render(request, 'customer/customer_portal.html') 

def business_portal(request):
  return render(request, 'business/business_portal.html')
  