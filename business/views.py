from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from customer.models import Admin, Customer, Feedback, Order
from django.contrib import messages
from business.models import Package, Shipment, Driver, Vehicle
from django.contrib.auth.models import User


def is_admin(user):
    return user.is_authenticated and hasattr(user, 'admin')

@login_required
def business_portal(request):
    packages = Package.objects.all().order_by('-created_at')
    orders = Order.objects.all().order_by('-created_at')
    customers = Customer.objects.all()
    drivers = Driver.objects.all()
    vehicles = Vehicle.objects.all()
    feedbacks = Feedback.objects.all()

    context = {
        'packages': packages,
        'orders': orders,
        'customers': customers,
        'drivers': drivers,
        'vehicles': vehicles,
        'feedbacks': feedbacks,
        'active_tab': request.GET.get('tab', 'Inventory'),
    }
    return render(request, 'business/business_portal.html', context)


def home(request):
    return render(request, 'home.html')


def handle_package_action(request):
    if request.method == 'POST':
        selected_packages = request.POST.getlist('selected_packages')
        action = request.POST.get('action')

        if action == 'delete':
            Package.objects.filter(id__in=selected_packages).delete()
            messages.success(request, "Selected packages have been removed.")
        elif action == 'update_status':
            new_status = request.POST.get('new_status')
            Package.objects.filter(id__in=selected_packages).update(status=new_status)
            messages.success(request, "Selected packages have been updated.")
        else:
            messages.error(request, "Invalid action.")

    return redirect('business:package-management')

@login_required
@user_passes_test(is_admin)
def update_package_status(request, package_id):
    package = get_object_or_404(Package, package_id=package_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        package.package_status = new_status
        package.save()
        messages.success(request, 'Package status updated successfully.')
    return redirect('business:business-portal')

@login_required
@user_passes_test(is_admin)
def create_shipment(request):
    if request.method == 'POST':
        package_ids = request.POST.getlist('package_ids')
        packages = Package.objects.filter(package_id__in=package_ids)
        shipment = Shipment.objects.create()
        for package in packages:
            package.shipment = shipment
            package.save()
        shipment.save()
    return redirect('business:business-portal')

@login_required
@user_passes_test(is_admin)
def inventory_view(request):
    packages = Package.objects.all()
    context = {'packages': packages, 'active_tab': 'Inventory'}
    return render(request, 'business/business_portal.html', context)

@login_required
@user_passes_test(is_admin)
def add_driver(request):
    if request.method == 'POST':
        driver_name = request.POST.get('driver_name')
        vehicle_id = request.POST.get('vehicle_id')
        vehicle = Vehicle.objects.get(vehicle_id=vehicle_id)
        Driver.objects.create(driver_name=driver_name, vehicle=vehicle)
        return redirect('business:business-portal')
    else:
        vehicles = Vehicle.objects.all()
        context = {'vehicles': vehicles}
        return render(request, 'business/add_driver.html', context)
    
@login_required
@user_passes_test(is_admin)
def create_shipment(request):
    if request.method == 'POST':
        package_ids = request.POST.getlist('package_ids')
        packages = Package.objects.filter(package_id__in=package_ids, package_status='Processing')
        if packages.exists():
            shipment = Shipment.objects.create()
            packages.update(shipment=shipment, package_status='Shipped')
            return redirect('business:business-portal')
        else:
            messages.error(request, 'No processing packages selected.')
    return redirect('business:business-portal')


@login_required
@user_passes_test(is_admin)
def add_vehicle(request):
    if request.method == 'POST':
        vehicle_model = request.POST.get('vehicle_model')
        vehicle_plate = request.POST.get('vehicle_plate')
        vehicle_status = request.POST.get('vehicle_status')
        Vehicle.objects.create(vehicle_model=vehicle_model, vehicle_plate=vehicle_plate, vehicle_status=vehicle_status)
        return redirect('business:business-portal')
    else:
        return render(request, 'business/add_vehicle.html')
    
@login_required
@user_passes_test(is_admin)
def create_shipment(request):
    if request.method == 'POST':
        package_ids = request.POST.getlist('package_ids')
        packages = Package.objects.filter(package_id__in=package_ids)
        shipment = Shipment.objects.create()
        for package in packages:
            package.shipment = shipment
            package.save()
        shipment.save()
    return redirect('business:business-portal')

@login_required
@user_passes_test(is_admin)
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        messages.success(request, 'Order status updated successfully.')
    return redirect('business:business-portal')




@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    packages = Package.objects.all()
    shipments = Shipment.objects.all()
    drivers = Driver.objects.all()
    vehicles = Vehicle.objects.all()
    context = {
        'packages': packages,
        'shipments': shipments,
        'drivers': drivers,
        'vehicles': vehicles,
    }
    return render(request, 'admin_dashboard.html', context)
