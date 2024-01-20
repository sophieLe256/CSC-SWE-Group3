from django.shortcuts import render

def business_portal(request):
    return render(request, 'business/business_portal.html')
