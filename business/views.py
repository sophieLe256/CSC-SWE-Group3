from django.shortcuts import render

def home(request):
  return render(request, 'home.html') 

def business_portal(request):
    return render(request, 'business/business_portal.html')


def inventory_view(request):
    packages = Package.objects.all()
    context = {
        'packages': packages 
    }
    return render(request, 'business/business_portal.html', context)