from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer, Package
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from customer.backends import EmailAuthenticationBackend
from .forms import OrderForm, ComplaintForm
from django.http import JsonResponse
from tracking.models import Shipment
from .forms import OrderForm
from .models import Feedback
from geopy.distance import geodesic
from .forms import OrderForm, FeedbackForm



def initialize_customer_data(request):
    cust = Customer.objects.first()
    return redirect('home')

def customer_options(request):
    return render(request, 'customer/customer_options.html')

def customer_signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists. Please login.')
            return redirect('customer-login')
        else:
            user = User.objects.create_user(username=email, email=email, password=password)
            Customer.objects.create(user_id=user.id, email=email)
            messages.success(request, 'Account created successfully. Please login.')
            return redirect('customer-login')
    return render(request, 'customer/customer_signup.html')

redirect_authenticated_user = True

def customer_login(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Use the EmailAuthenticationBackend to authenticate the user
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('customer-dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
            return render(request, 'customer/customer_login.html')
    else:
        return render(request, 'customer/customer_login.html')

@login_required
def customer_profile(request):
    customer = Customer.objects.get(user_id=request.user.id)
    context = {
        'customer': customer
    }
    return render(request, 'customer/customer_profile.html', context)

@login_required
def customer_dashboard(request):
    customer = get_object_or_404(Customer, user_id=request.user.id)
    active_orders = Order.objects.filter(customer=customer, status='Processing')
    past_orders = Order.objects.filter(customer=customer).exclude(status='Processing')
    active_shipments = Shipment.objects.filter(customer=customer, status='Processing')

    order_form = OrderForm()
    feedback_form = FeedbackForm()

    if request.method == 'POST':
        if 'order_form' in request.POST:
            order_form = OrderForm(request.POST)
            if order_form.is_valid():
                order = Order.objects.create(
                    customer=customer,
                    package_dimensions=order_form.cleaned_data['package_dimensions'],
                    package_weight=order_form.cleaned_data['package_weight'],
                    pickup_or_dropoff=order_form.cleaned_data['pickup_or_dropoff'],
                    estimated_cost=calculate_estimated_cost(
                        order_form.cleaned_data['package_dimensions'],
                        order_form.cleaned_data['package_weight'],
                        order_form.cleaned_data['pickup_or_dropoff']
                    )['total'],
                    status='Processing'
                )
                Shipment.objects.create(
                    tracking_number=generate_tracking_number(),
                    package_description=f'Order #{order.order_number}',
                    pickup_address=customer.address,
                    delivery_address=customer.address,
                    customer=customer,
                    status='Processing'
                )
                return redirect('customer-dashboard')
        elif 'feedback_form' in request.POST:
            feedback_form = FeedbackForm(request.POST)
            if feedback_form.is_valid():
                feedback = feedback_form.save(commit=False)
                feedback.customer = customer
                feedback.save()
                return redirect('customer-dashboard')

    context = {
        'order_form': order_form,
        'feedback_form': feedback_form,
        'active_orders': active_orders,
        'past_orders': past_orders,
        'active_shipments': active_shipments,
        'customer': customer
    }
    return render(request, 'customer/customer_dashboard.html', context)



def calculate_estimated_cost(height, width, length, address, shipping_type):
    volume = height * width * length
    base_cost = volume * 0.5
    shipping_cost = get_shipping_cost(shipping_type, address)
    handling_cost = 5.0
    subtotal = base_cost + shipping_cost + handling_cost
    tax = subtotal * 0.1
    total = subtotal + tax

    return {
        'shipping': shipping_cost,
        'handling': handling_cost,
        'subtotal': subtotal,
        'tax': tax,
        'total': total
    }

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            customer = Customer.objects.get(user_id=request.user.id)
            feedback = form.save(commit=False)
            feedback.customer = customer
            feedback.save()
            messages.success(request, 'Feedback submitted successfully.')
            return redirect('customer-dashboard')
    else:
        form = FeedbackForm()
    return render(request, 'customer/feedback_form.html', {'form': form})



def get_shipping_cost(shipping_type, address):
    # Implement a realistic shipping cost calculation based on the address
    # and the shipping type
    if shipping_type == 'ground':
        return 10.0
    elif shipping_type == 'priority':
        return 20.0
    elif shipping_type == 'nextDay':
        return 30.0
    else:
        return 0.0

def customer_logout(request):
    logout(request)
    return redirect('home')

def calculate_estimated_cost(height, width, length, shipping_type):
    volume = height * width * length
    base_cost = volume * 0.5
    shipping_cost = get_shipping_cost(shipping_type)
    handling_cost = 5.0
    subtotal = base_cost + shipping_cost + handling_cost
    tax = subtotal * 0.1
    total = subtotal + tax

    return {
        'shipping': shipping_cost,
        'handling': handling_cost,
        'subtotal': subtotal,
        'tax': tax,
        'total': total
    }

def get_shipping_cost(shipping_type):
    if shipping_type == 'ground':
        return 10.0
    elif shipping_type == 'priority':
        return 20.0
    elif shipping_type == 'nextDay':
        return 30.0
    else:
        return 0.0

def process_complaint(complaint):
    pass

@login_required
def place_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            customer = Customer.objects.get(user_id=request.user.id)
            order = Order.objects.create(
                customer=customer,
                package_dimensions=form.cleaned_data['package_dimensions'],
                package_weight=form.cleaned_data['package_weight'],
                pickup_or_dropoff=form.cleaned_data['pickup_or_dropoff'],
                estimated_cost=calculate_estimated_cost(
                    form.cleaned_data['package_dimensions'],
                    form.cleaned_data['package_weight']
                )['total']
            )
            # Handle payment and create shipment
            shipment = Shipment.objects.create(
                tracking_number=generate_tracking_number(),
                package_description=f'Order #{order.order_number}',
                pickup_address=customer.address,
                delivery_address=customer.address,
                customer=customer
            )
            return redirect('customer-dashboard')
    else:
        form = OrderForm()
    return render(request, 'customer/order_form.html', {'form': form})



@login_required
def customer_profile(request):
    customer = Customer.objects.get(user_id=request.user.id)
    if request.method == 'POST':
        # Update customer profile information
        customer.first_name = request.POST.get('first_name')
        customer.last_name = request.POST.get('last_name')
        customer.address = request.POST.get('address')
        customer.phone = request.POST.get('phone')
        customer.save()
        messages.success(request, 'Profile updated successfully.')
    return render(request, 'customer/customer_profile.html', {'customer': customer})


@login_required
def admin_profile(request):
    customer = Customer.objects.get(user_id=request.user.id)
    if customer.is_admin:
        if request.method == 'POST':
            # Update admin profile information
            customer.first_name = request.POST.get('first_name')
            customer.last_name = request.POST.get('last_name')
            customer.address = request.POST.get('address')
            customer.phone = request.POST.get('phone')
            customer.save()
            messages.success(request, 'Profile updated successfully.')
        return render(request, 'admin/admin_profile.html', {'customer': customer})
    else:
        return redirect('customer-profile')


@login_required
def track_shipment(request):
    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number')
        try:
            shipment = Shipment.objects.get(tracking_number=tracking_number, customer__user_id=request.user.id)
            return render(request, 'customer/shipment_status.html', {'shipment': shipment})
        except Shipment.DoesNotExist:
            return render(request, 'customer/shipment_status.html', {'error': 'Invalid tracking number.'})
    return render(request, 'customer/track_shipment.html')

