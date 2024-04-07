from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from customer.models import Customer, Order
from django.core.exceptions import ObjectDoesNotExist


class TrackOrderTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a customer user
        self.customer_user = User.objects.create_user(username='customer', email='customer@example.com', password='password123')
        # Create a customer profile
        self.customer = Customer.objects.create(user_id=self.customer_user.id, first_name='John', last_name='Doe', email='customer@example.com')
        # Create an order
        self.order = Order.objects.create(order_number='123456', customer=self.customer, package_weight=10.0, status='Processing',estimated_cost=0.0)

    def test_track_order_with_valid_tracking_number(self):
        # Simulate a POST request with a valid tracking number
        response = self.client.post(reverse('package-status'), {'tracking_number': self.order.order_number})
        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Assert that the order number is present in the response content
        self.assertContains(response, 'Tracking Number: 123456')
        
class TrackOrderInvalidTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a customer user
        self.customer_user = User.objects.create_user(username='customer', email='customer@example.com', password='password123')
        # Create a customer profile
        self.customer = Customer.objects.create(user_id=self.customer_user.id, first_name='John', last_name='Doe', email='customer@example.com')
        # Create an order
        self.order = Order.objects.create(order_number='123456', customer=self.customer, package_weight=10.0, status='Processing', estimated_cost=0.0)

    def test_track_order_with_invalid_tracking_number(self):
        # Create a client and simulate a POST request with an invalid tracking number
        client = Client()
        response = client.post(reverse('package-status'), {'tracking_number': 'invalid_tracking_number'})

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the error message for invalid tracking number is present in the response content
        self.assertContains(response, 'Invalid tracking number.')
