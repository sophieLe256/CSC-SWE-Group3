from .models import CustomerServiceMessage
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer, Package, Order, Feedback
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from customer.backends import EmailAuthenticationBackend
from .forms import OrderForm, ComplaintForm, FeedbackForm
from django.http import JsonResponse
from tracking.models import Shipment
from geopy.distance import geodesic
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import Customer, Admin
from django.shortcuts import redirect
import random
import string
from decimal import Decimal
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone


@login_required
def submit_customer_service_message(request):
    if request.method == 'POST':
        customer = Customer.objects.get(user_id=request.user.id)
        message = request.POST.get('message')
        CustomerServiceMessage.objects.create(
            customer=customer,
            message=message,
            status='Open'
        )
        return redirect('customer-dashboard')
    return redirect('customer-dashboard')


print('Trying to reverse URL: business-portal')
def generate_temporary_password(length=8):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('customer-dashboard')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'customer/change_password.html', {'form': form})

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            customer = Customer.objects.get(email=email)
            temporary_password = generate_temporary_password()
            customer.user.set_password(temporary_password)
            customer.user.save()
            subject = 'Temporary Password'
            message = f'Your temporary password is: {temporary_password}'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
            messages.success(request, 'A temporary password has been sent to your email.')
            return redirect('customer-login')
        except Customer.DoesNotExist:
            messages.error(request, 'No account found with that email.')
    return render(request, 'customer/forgot_password.html')


@login_required
def customer_logout(request):
    logout(request)
    request.session.flush()
    return redirect('home')

def initialize_customer_data(request):
    cust = Customer.objects.first()
    return redirect('home')


def customer_options(request):
    return render(request, 'customer/customer_options.html')

def customer_signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')

        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"User Type: {user_type}")

        if User.objects.filter(email=email).exists():
            print("Email already exists.")
            messages.error(request, 'Email already exists. Please login.')
            return redirect('customer-login')
        else:
            user = User.objects.create_user(username=email, email=email, password=password)
            print(f"User created: {user}")

            if user_type == 'customer':
                Customer.objects.create(user_id=user.id, email=email)
                print("Customer object created.")
            elif user_type == 'admin':
                Admin.objects.create(user_id=user.id, email=email)
                print("Admin object created.")
            else:
                print("Invalid user type.")
                messages.error(request, 'Invalid user type.')
                return redirect('customer-signup')
            
            authenticated_user = authenticate(request, username=email, password=password)
            
            if authenticated_user is not None:
                print("User authenticated successfully.")
                login(request, authenticated_user)
                
                if user_type == 'customer':
                    print("Redirecting to customer dashboard.")
                    return redirect('customer-dashboard')
                elif user_type == 'admin':
                    print("Redirecting to business portal.")
                    return redirect('business:business-portal')
            else:
                print("User authentication failed.")
                messages.error(request, 'Failed to authenticate the user.')
    
    return render(request, 'customer/customer_signup.html')


def customer_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            try:
                customer = Customer.objects.get(user_id=user.id)
                request.session['user_type'] = 'customer'
                return redirect('customer-dashboard')
            except Customer.DoesNotExist:
                try:
                    admin = Admin.objects.get(user_id=user.id)
                    request.session['user_type'] = 'admin'
                    return redirect('business:business-portal')
                except Admin.DoesNotExist:
                    messages.error(request, 'Invalid user.')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'customer/customer_login.html')



@login_required
def customer_profile(request):
    customer = Customer.objects.get(user_id=request.user.id)
    context = {
        'customer': customer
    }
    return render(request, 'customer/customer_profile.html', context)

@login_required
def place_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            customer = Customer.objects.get(user_id=request.user.id)
            height = form.cleaned_data['height']
            width = form.cleaned_data['width']
            length = form.cleaned_data['length']
            package_weight = form.cleaned_data['package_weight']
            pickup_or_dropoff = form.cleaned_data['pickup_or_dropoff']
            pickup_address = form.cleaned_data['pickup_address']
            delivery_address = form.cleaned_data['delivery_address']
            shipping_type = form.cleaned_data['shipping_type']

            print(f"Form data: Height={height}, Width={width}, Length={length}, Weight={package_weight}, PickupOrDropoff={pickup_or_dropoff}, PickupAddress={pickup_address}, DeliveryAddress={delivery_address}, ShippingType={shipping_type}")

            estimated_cost_data = calculate_estimated_cost(height, width, length, package_weight, pickup_or_dropoff, shipping_type)
            if 'estimate' in request.POST:
                print("Estimate requested")
                return JsonResponse(estimated_cost_data)
            else:
                print("Placing order")
                current_date = timezone.now().strftime('%Y%m%d')
                random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                order_number = f"{current_date}-{random_chars}"
                
                order = Order.objects.create(
                    order_number=order_number,
                    customer=customer,
                    height=height,
                    width=width,
                    length=length,
                    package_weight=package_weight,
                    pickup_or_dropoff=pickup_or_dropoff,
                    pickup_address=pickup_address,
                    delivery_address=delivery_address,
                    shipping_type=shipping_type,
                    estimated_cost=estimated_cost_data['total'],
                    status='Processing'
                )
                print(f"Order created: {order}")
                return redirect('customer-dashboard')
    else:
        form = OrderForm()

    print("Rendering order form")
    return render(request, 'customer/order_form.html', {'form': form})


@login_required
def customer_dashboard(request):
    print(f"User: {request.user}")
    print(f"User type: {request.session.get('user_type')}")

    if request.session.get('user_type') != 'customer':
        print("User type is not customer")
        return redirect('customer-login')   
    try:
        customer = Customer.objects.get(user_id=request.user.id)
    except Customer.DoesNotExist:
        messages.error(request, 'User does not exist.')
        print("Customer does not exist")
        return redirect('customer-login')
    
    active_tab = request.GET.get('tab', 'Orders')  # Set default active tab to 'Orders'
    active_orders = Order.objects.filter(customer=customer, status='Processing').order_by('-created_at')
    past_orders = Order.objects.filter(customer=customer).exclude(status='Processing').order_by('-created_at')
    customer_service_messages = CustomerServiceMessage.objects.filter(customer=customer)

    order_form = OrderForm()

    if request.method == 'POST':
        if 'order_form' in request.POST:
            order_form = OrderForm(request.POST)
            if order_form.is_valid():
                order = Order.objects.create(
                    customer=customer,
                    height=order_form.cleaned_data['height'],
                    width=order_form.cleaned_data['width'],
                    length=order_form.cleaned_data['length'],
                    package_weight=order_form.cleaned_data['package_weight'],
                    pickup_or_dropoff=order_form.cleaned_data['pickup_or_dropoff'],
                    pickup_address=order_form.cleaned_data['pickup_address'],
                    delivery_address=order_form.cleaned_data['delivery_address'],
                    shipping_type=order_form.cleaned_data['shipping_type'],
                    estimated_cost=calculate_estimated_cost(
                        order_form.cleaned_data['height'],
                        order_form.cleaned_data['width'],
                        order_form.cleaned_data['length'],
                        order_form.cleaned_data['package_weight'],
                        order_form.cleaned_data['pickup_or_dropoff'],
                        order_form.cleaned_data['shipping_type']
                    )['total'],
                    status='Processing'
                )
                Shipment.objects.create(
                    tracking_number=order.order_number,
                    package_description=f'Order #{order.order_number}',
                    pickup_address=order.pickup_address,
                    delivery_address=order.delivery_address,
                    customer=customer,
                    status='Processing'
                )
                return redirect('customer-dashboard')
        elif 'customer_service_form' in request.POST:
            message = request.POST.get('message')
            CustomerServiceMessage.objects.create(
                customer=customer,
                message=message,
                status='Open'
            )
            return redirect('customer-dashboard')

    context = {
        'order_form': order_form,
        'active_orders': active_orders,
        'past_orders': past_orders,
        'customer_service_messages': customer_service_messages,
        'customer': customer,
        'active_tab': active_tab,
    }
    print("Rendering customer dashboard")
    return render(request, 'customer/customer_dashboard.html', context)




def calculate_estimated_cost(height, width, length, package_weight, pickup_or_dropoff, shipping_type):
    # Calculate volume
    volume = Decimal(height) * Decimal(width) * Decimal(length)

    # Implement a realistic shipping cost calculation based on the package dimensions, weight, pickup or dropoff, and shipping type
    if pickup_or_dropoff == 'pickup':
        if shipping_type == 'ground':
            shipping_cost = Decimal('10.0')
        elif shipping_type == 'priority':
            shipping_cost = Decimal('15.0')
        elif shipping_type == 'nextDay':
            shipping_cost = Decimal('20.0')
        else:
            shipping_cost = Decimal('0.0')
    elif pickup_or_dropoff == 'dropoff':
        if shipping_type == 'ground':
            shipping_cost = Decimal('12.0')
        elif shipping_type == 'priority':
            shipping_cost = Decimal('17.0')
        elif shipping_type == 'nextDay':
            shipping_cost = Decimal('22.0')
        else:
            shipping_cost = Decimal('0.0')
    else:
        shipping_cost = Decimal('0.0')

    base_cost = Decimal(package_weight) * Decimal('0.5')
    handling_cost = Decimal('5.0')
    subtotal = base_cost + shipping_cost + handling_cost
    tax = subtotal * Decimal('0.1')
    total = subtotal + tax

    print(f"Calculated estimated cost: Shipping={shipping_cost}, Handling={handling_cost}, Subtotal={subtotal}, Tax={tax}, Total={total}")

    return {
        'shipping': float(shipping_cost),
        'handling': float(handling_cost),
        'subtotal': float(subtotal),
        'tax': float(tax),
        'total': float(total)
    }

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            customer = Customer.objects.get(email=email)
            user = User.objects.get(id=customer.user_id)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(f'/customer/reset-password/{uid}/{token}/')
            subject = 'Reset Your Password'
            message = render_to_string('customer/reset_password_email.html', {
                'user': user,
                'reset_url': reset_url
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
            messages.success(request, 'Password reset email has been sent.')
            return redirect('customer-login')
        except Customer.DoesNotExist:
            messages.error(request, 'No account found with that email.')
    return render(request, 'customer/forgot_password.html')


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


def calculate_estimated_cost(height, width, length, package_weight, pickup_or_dropoff, shipping_type):
    # Calculate volume
    volume = Decimal(height) * Decimal(width) * Decimal(length)

    # Implement a realistic shipping cost calculation based on the package dimensions, weight, pickup or dropoff, and shipping type
    if pickup_or_dropoff == 'pickup':
        if shipping_type == 'ground':
            shipping_cost = Decimal('10.0')
        elif shipping_type == 'priority':
            shipping_cost = Decimal('15.0')
        elif shipping_type == 'nextDay':
            shipping_cost = Decimal('20.0')
        else:
            shipping_cost = Decimal('0.0')
    elif pickup_or_dropoff == 'dropoff':
        if shipping_type == 'ground':
            shipping_cost = Decimal('12.0')
        elif shipping_type == 'priority':
            shipping_cost = Decimal('17.0')
        elif shipping_type == 'nextDay':
            shipping_cost = Decimal('22.0')
        else:
            shipping_cost = Decimal('0.0')
    else:
        shipping_cost = Decimal('0.0')

    base_cost = Decimal(package_weight) * Decimal('0.5')
    handling_cost = Decimal('5.0')
    subtotal = base_cost + shipping_cost + handling_cost
    tax = subtotal * Decimal('0.1')
    total = subtotal + tax

    print(f"Calculated estimated cost: Shipping={shipping_cost}, Handling={handling_cost}, Subtotal={subtotal}, Tax={tax}, Total={total}")

    return {
        'shipping': float(shipping_cost),
        'handling': float(handling_cost),
        'subtotal': float(subtotal),
        'tax': float(tax),
        'total': float(total)
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

def business_portal(request):
    packages = Package.objects.all().order_by('-created_at')
    user_type = request.session.get('user_type')
    if user_type == 'admin':
        try:
            admin = Admin.objects.get(user_id=request.user.id)
            return render(request, 'business/business_portal.html')
        except Admin.DoesNotExist:
            messages.error(request, 'This account is not associated with an admin.')
            return redirect('customer-login')
    else:
        messages.error(request, 'You are not authorized to access the business portal.')
        return redirect('customer-dashboard')


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