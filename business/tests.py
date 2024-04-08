from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from customer.models import Customer, Order
from customer.models import Admin
from django.contrib.auth import authenticate

class AdminEditOrderStatusTestCase(TestCase):
    def setUp(self):
        self.business_email = "business@example.com"
        self.business_password = "Password456?"
        # Create a business user
        self.business_user = User.objects.create_user(username=self.business_email, email=self.business_email, password=self.business_password)
        # Create a business profile
        self.business_profile = Admin.objects.create(user_id=self.business_user.id, email=self.business_email)
        
    def test_update_order_status(self):
        # Log in the admin user
        self.client.login(username=self.business_email, password=self.business_password)

        # Create a customer user and order
        customer_user = User.objects.create_user(username='customer', email='customer@example.com', password='password123')
        customer = Customer.objects.create(user_id=customer_user.id, first_name='John', last_name='Doe', email='customer@example.com')
        order = Order.objects.create(order_number='123456', customer=customer, package_weight=10.0, status='Processing',estimated_cost=0.0)

        # Simulate a POST request to change the order status
        new_status = 'Shipped'
        response = self.client.post(reverse('business:update-order-status', kwargs={'order_id': order.id}), {'status': new_status})
        
        # Refresh the order from the database
        updated_order = Order.objects.get(id=order.id)

        # Assert that the response status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)

        # Assert that the order status has been updated
        self.assertEqual(updated_order.status, new_status)

class OrderFulfillmentTest(TestCase):
    def setUp(self):
        self.business_email = "business@example.com"
        self.business_password = "Password456?"
        # Create a business user
        self.business_user = User.objects.create_user(username=self.business_email, email=self.business_email, password=self.business_password)
        # Create a business profile
        self.business_profile = Admin.objects.create(user_id=self.business_user.id, email=self.business_email)
        
    def test_update_order_status(self):
        # Log in the admin user
        self.client.login(username=self.business_email, password=self.business_password)

        # Create a customer user and order
        customer_user = User.objects.create_user(username='customer', email='customer@example.com', password='password123')
        customer = Customer.objects.create(user_id=customer_user.id, first_name='John', last_name='Doe', email='customer@example.com')
        order = Order.objects.create(order_number='123456', customer=customer, package_weight=10.0, status='Processing',estimated_cost=0.0)

        # Simulate a POST request to change the order status to delivered 
        new_status = 'Delivered'
        response = self.client.post(reverse('business:update-order-status', kwargs={'order_id': order.id}), {'status': new_status})
        
        # Refresh the order from the database
        updated_order = Order.objects.get(id=order.id)

        # Assert that the response status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)

        # Assert that the order status has been updated
        self.assertEqual(updated_order.status, new_status)

class OrderCancellationByAdminTest(TestCase):
    def setUp(self):
        self.business_email = "business@example.com"
        self.business_password = "Password456?"
        # Create a business user
        self.business_user = User.objects.create_user(username=self.business_email, email=self.business_email, password=self.business_password)
        # Create a business profile
        self.business_profile = Admin.objects.create(user_id=self.business_user.id, email=self.business_email)
        
    def test_update_order_status(self):
        # Log in the admin user
        self.client.login(username=self.business_email, password=self.business_password)

        # Create a customer user and order
        customer_user = User.objects.create_user(username='customer', email='customer@example.com', password='password123')
        customer = Customer.objects.create(user_id=customer_user.id, first_name='John', last_name='Doe', email='customer@example.com')
        order = Order.objects.create(order_number='123456', customer=customer, package_weight=10.0, status='Processing',estimated_cost=0.0)

        # Simulate a POST request to change the order status to cancelled 
        new_status = 'Cancelled'
        response = self.client.post(reverse('business:update-order-status', kwargs={'order_id': order.id}), {'status': new_status})
        
        # Refresh the order from the database
        updated_order = Order.objects.get(id=order.id)

        # Assert that the response status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)

        # Assert that the order status has been updated
        self.assertEqual(updated_order.status, new_status)