from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from customer.models import Admin, Customer, Feedback, Order, CustomerServiceMessage
from django.contrib import messages
from business.models import Package, Shipment, Driver, Vehicle
from django.contrib.auth.models import User
from django.urls import reverse 
from decimal import Decimal, InvalidOperation
from django.utils import timezone


def is_admin(user):
    return user.is_authenticated and Admin.objects.filter(user_id=user.id).exists()
    

@login_required
@user_passes_test(is_admin)
def business_portal(request):
    packages = Package.objects.all().order_by('-created_at')
    orders = Order.objects.all().order_by('-created_at')
    customers = Customer.objects.all()
    drivers = Driver.objects.all()
    vehicles = Vehicle.objects.all()
    feedbacks = Feedback.objects.all()
    customer_service_messages = CustomerServiceMessage.objects.all().order_by('-created_at') 

    if 'create_vehicle' in request.POST:
        vehicle_model = request.POST.get('vehicle_model')
        vehicle_plate = request.POST.get('vehicle_plate')
        vehicle_status = request.POST.get('vehicle_status')
        volume_capacity = request.POST.get('volume_capacity')
        weight_capacity = request.POST.get('weight_capacity')
        
        if vehicle_model and vehicle_plate and vehicle_status and volume_capacity and weight_capacity:
            try:
                volume_capacity = Decimal(volume_capacity)
                weight_capacity = Decimal(weight_capacity)
                
                Vehicle.objects.create(
                    vehicle_model=vehicle_model,
                    vehicle_plate=vehicle_plate,
                    vehicle_status=vehicle_status,
                    volume_capacity=volume_capacity,
                    weight_capacity=weight_capacity
                )
            except (ValueError, InvalidOperation):
                messages.error(request, 'Invalid volume or weight capacity. Please enter valid decimal values.')
        else:
            messages.error(request, 'All fields are required.')
    elif 'remove_vehicle' in request.POST:
        vehicle_id = request.POST.get('vehicle_id')
        Vehicle.objects.filter(vehicle_id=vehicle_id).delete()



    context = {
        'packages': packages,
        'orders': orders,
        'customers': customers,
        'drivers': drivers,
        'vehicles': vehicles,
        'feedbacks': feedbacks,
        'customer_service_messages': customer_service_messages,
        'active_tab': request.GET.get('tab', 'Inventory'),
        
    }
    return render(request, 'business/business_portal.html', context)



def home(request):
    return render(request, 'home.html')

@login_required
@user_passes_test(is_admin)
def assign_package_to_vehicle(request, package_id):
    package = get_object_or_404(Package, package_id=package_id)
    vehicles = Vehicle.objects.filter(status='Available').order_by('available_space')
    
    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle_id')
        vehicle = get_object_or_404(Vehicle, vehicle_id=vehicle_id)
        
        if vehicle.available_space >= package.package_weight:
            package.vehicle = vehicle
            package.package_status = 'shipped'
            package.save()
            
            vehicle.available_space -= package.package_weight
            vehicle.save()
            
            messages.success(request, 'Package assigned to vehicle successfully.')
        else:
            messages.error(request, 'Insufficient space in the selected vehicle.')
        
        return redirect('business:business-portal')
    
    context = {'package': package, 'vehicles': vehicles}
    return render(request, 'business/assign_package_to_vehicle.html', context)


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
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()

        # Update the package status and send the email
        package = order.package_set.first()
        if package:
            old_status = package.package_status
            package.package_status = new_status
            if new_status == 'Delivered':
                package.delivered_at = timezone.now()
            package.save()

            if package.customer.email_verified and package.customer.notification_preference and new_status != old_status:
                subject = 'Package Status Update'
                html_message = render_to_string('customer/package_status_notification.html', {'package': package})
                plain_message = strip_tags(html_message)
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = package.customer.email
                send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

    return redirect('business:business-portal')

@login_required
@user_passes_test(is_admin)
def update_package_status(request, package_id):
    package = get_object_or_404(Package, package_id=package_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        old_status = package.package_status
        package.package_status = new_status
        if new_status == 'Delivered':
            package.delivered_at = timezone.now()
        package.save()

        if package.customer.email_verified and package.customer.notification_preference and new_status != old_status:
            subject = 'Package Status Update'
            html_message = render_to_string('customer/package_status_notification.html', {'package': package})
            plain_message = strip_tags(html_message)
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = package.customer.email
            send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

        messages.success(request, 'Package status updated successfully.')
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
        
        vehicle = get_object_or_404(Vehicle, vehicle_id=vehicle_id) 
        # vehicle = Vehicle.objects.get(vehicle_id=vehicle_id)
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
        data = json.loads(request.body)
        shipment_id = data.get('shipmentId')
        package_ids = data.get('package_ids')
        vehicle_id = data.get('vehicle_id')

        vehicle = get_object_or_404(Vehicle, vehicle_id=vehicle_id)

        # If creating a new shipment
        if shipment_id == 'new':
            shipment = Shipment.objects.create(vehicle=vehicle)
        else:
            shipment = get_object_or_404(Shipment, id=shipment_id)

        packages = Package.objects.filter(package_id__in=package_ids, package_status='Processing')
        if packages.exists():
            for package in packages:
                package.shipment = shipment
                # No need to set customer_email here since it's already part of the Package model and should not be modified in this context.
                package.save()
            packages.update(package_status='Shipped')
            messages.success(request, 'Shipment created and packages updated successfully.')
            return redirect('business:business-portal')
        else:
            messages.error(request, 'No processing packages selected.')
    vehicle = get_object_or_404(Vehicle, vehicle_id=vehicle_id)

    if not vehicle.driver:
        return JsonResponse({'error': 'Vehicle does not have a driver assigned'})

    total_volume = sum(package.package_dimensions.split('x')[0] * package.package_dimensions.split('x')[1] * package.package_dimensions.split('x')[2] for package in packages)
    total_weight = sum(package.package_weight for package in packages)

    if total_volume > vehicle.available_volume or total_weight > vehicle.available_weight:
        return JsonResponse({'error': 'Vehicle capacity exceeded'})

    vehicle.available_volume -= total_volume
    vehicle.available_weight -= total_weight
    vehicle.save()

    packages.update(shipment=shipment, package_status='Dispatched')
    shipment.vehicle = vehicle
    shipment.save()

    package_ids = list(packages.values_list('package_id', flat=True))
    return JsonResponse({'shipmentId': shipment.id, 'packageIds': package_ids})





@login_required
@user_passes_test(is_admin)
def add_vehicle(request):
    if request.method == 'POST':
        vehicle_model = request.POST.get('vehicle_model')
        vehicle_plate = request.POST.get('vehicle_plate')
        vehicle_status = request.POST.get('vehicle_status')
        volume_capacity = request.POST.get('volume_capacity')
        weight_capacity = request.POST.get('weight_capacity')
        
        try:
            Vehicle.objects.create(
                vehicle_model=vehicle_model,
                vehicle_plate=vehicle_plate,
                vehicle_status=vehicle_status,
                volume_capacity=Decimal(volume_capacity),
                weight_capacity=Decimal(weight_capacity)
            )
            messages.success(request, 'Vehicle added successfully.')
        except (ValueError, InvalidOperation):
            messages.error(request, 'Invalid volume or weight capacity. Please enter valid decimal values.')
        
        return redirect('business:business-portal', tab='Vehicles')
    
    return redirect('business:business-portal', tab='Vehicles')



  
@login_required
@user_passes_test(is_admin)
def add_driver(request):
    if request.method == 'POST':
        driver_name = request.POST.get('driver_name')
        vehicle_id = request.POST.get('vehicle_id')
        
        vehicle = get_object_or_404(Vehicle, vehicle_id=vehicle_id) 
        # vehicle = Vehicle.objects.get(vehicle_id=vehicle_id)
        Driver.objects.create(driver_name=driver_name, vehicle=vehicle)
        return redirect('business:business-portal')
    else:
        vehicles = Vehicle.objects.all()
        context = {'vehicles': vehicles}
        return render(request, 'business/add_driver.html', context)


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
