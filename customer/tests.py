from django.test import TestCase, Client 
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Customer, Admin, CustomerServiceMessage, Feedback, Order
from django.core.exceptions import ValidationError

class CustomerLoginTestCase(TestCase):
    def setUp(self):
        self.customer_email = "customer@example.com"
        self.customer_password = "Password123*"
        # Create a customer user
        self.customer_user = User.objects.create_user(username=self.customer_email, email=self.customer_email, password=self.customer_password)
        # Create a customer profile
        self.customer_profile = Customer.objects.create(user_id=self.customer_user.id, email=self.customer_email)

    def test_customer_login(self):
        # Navigate to the login page
        login_url = reverse('customer-login')
        response = self.client.get(login_url)
        self.assertEqual(response.status_code, 200)

        # Attempt to login with customer credentials
        login_data = {
            'email': self.customer_email,
            'password': self.customer_password
        }
        response = self.client.post(login_url, login_data, follow=True)

        # Check if the user is redirected to the customer dashboard
        self.assertRedirects(response, reverse('customer-dashboard'))

class BusinessLoginTestCase(TestCase):
    def setUp(self):
        self.business_email = "business@example.com"
        self.business_password = "Password456?"
        # Create a business user
        self.business_user = User.objects.create_user(username=self.business_email, email=self.business_email, password=self.business_password)
        # Create a business profile
        self.business_profile = Admin.objects.create(user_id=self.business_user.id, email=self.business_email)

    def test_business_login(self):
        # Navigate to the login page
        login_url = reverse('customer-login')
        response = self.client.get(login_url)
        self.assertEqual(response.status_code, 200)

        # Attempt to login with business credentials
        login_data = {
            'email': self.business_email,
            'password': self.business_password
        }
        response = self.client.post(login_url, login_data, follow=True)

        # Check if the user is redirected to the business dashboard
        self.assertRedirects(response, reverse('business:business-portal'))
        
class IncorrectCredentialsLoginTestCase(TestCase):
    def test_incorrect_credentials_login(self):
        # Navigate to the login page
        login_url = reverse('customer-login')
        response = self.client.get(login_url)
        self.assertEqual(response.status_code, 200)
        # Attempt to login with incorrect credentials
        login_data = {
            'username': 'non_existing_user@example.com',
            'password': 'incorrect_password'
            }
        response = self.client.post(login_url, login_data, follow=True)
        # Check if the user is redirected back to the login page with error message
        self.assertEqual(response.status_code, 200)  # Ensure the response is successful
        self.assertContains(response, "Invalid email or password.")  # Check for error message

class CustomerSignupTestCase(TestCase):
    def test_customer_signup(self):
        # Ensure no user exists with the provided email
        new_email = 'test@example.com'
        self.assertFalse(User.objects.filter(email=new_email).exists())
        # Test setup: Navigate to the registration page
        signup_url = reverse('customer-signup')
        
        response = self.client.get(signup_url)
        self.assertEqual(response.status_code, 200)  # Check if the registration page is accessible
        
        # Test: Attempt to create a new account with valid information
        valid_data={
            'email': new_email, 
            'password1': 'Password123*',
            'password2': 'Password123*', 
            'user_type': 'customer', 
        }
        response = self.client.post(signup_url, valid_data, follow=True)
        # Assert that the response is a redirect to the customer login page
        self.assertRedirects(response, reverse('customer-login'))
        # Check if the user account was created
        self.assertTrue(User.objects.filter(email=new_email).exists())
        
class InvalidSignupTestCase(TestCase):
    def test_invalid_customer_signup(self):
        # Navigate to the registration page 
        signup_url = reverse('customer-signup')
        response = self.client.get(signup_url)
        self.assertEqual(response.status_code, 200)
        
        invalid_data= {
            'email': 'invalidemail', 
            'password1': 'weak', 
            'password2': 'weak', 
            'user_type': 'customer', 
        }
        # Submit the form with invalid data
        response = self.client.post(signup_url, invalid_data, follow=False)


class ExistingEmailSignupTestCase(TestCase):
    def setUp(self):
        # Create a user with an existing email
        self.existing_email = 'existing@example.com'
        self.existing_user = User.objects.create_user(username=self.existing_email, email=self.existing_email, password='password123')

    def test_existing_email_signup(self):
        # Navigate to the registration page
        signup_url = reverse('customer-signup')
        response = self.client.get(signup_url)
        self.assertEqual(response.status_code, 200)

        # Attempt to sign up with an existing email
        existing_email_data = {
            'email': self.existing_email,
            'password': 'Newpassword123*',
            'user_type': 'customer',
        }
        response = self.client.post(signup_url, existing_email_data)

        # Verify that the user is redirected to the login page
        self.assertRedirects(response, reverse('customer-login'))

        
class SubmitCustomerServiceMessageTestCase(TestCase):
    def setUp(self):
        # Create a customer user
        self.customer_user = User.objects.create_user(username='customer', email='customer@example.com', password='password123')

        # Create a customer profile
        self.customer = Customer.objects.create(user_id=self.customer_user.id, first_name='John', last_name='Doe', email='customer@example.com')

    def test_submit_customer_service_message(self):
        # Simulate customer submitting feedback
        self.client.login(username='customer', password='password123')
        response = self.client.post(reverse('submit-customer-service-message'), {'message': 'Excellent service!'})

        # Check feedback submission
        self.assertEqual(response.status_code, 302)  # Assuming a successful redirect after submission
        self.assertTrue(CustomerServiceMessage.objects.filter(customer=self.customer, message='Excellent service!', status='Open').exists())
        self.assertTrue(Feedback.objects.filter(customer=self.customer, comment='Excellent service!').exists())
        
class SubmitEmptyCustomerServiceMessageTestCase(TestCase):
    def setUp(self):
        # Create a customer user
        self.customer_user = User.objects.create_user(username='customer', email='customer@example.com', password='password123')

        # Create a customer profile
        self.customer = Customer.objects.create(user_id=self.customer_user.id, first_name='John', last_name='Doe', email='customer@example.com')

    def test_submit_empty_customer_service_message(self):
        # Simulate customer submitting an empty message
        self.client.login(username='customer', password='password123')
        response = self.client.post(reverse('submit-customer-service-message'), {'message': ''})  # Sending empty string

        # Check behavior for empty message
        # Assert that it returns a bad request status code
        self.assertEqual(response.status_code, 400)  
            
class CustomerOrdersTestCase(TestCase):
    def setUp(self):
        # Create a customer user
        self.customer_user = User.objects.create_user(username='customer', email='customer@example.com', password='password123')

        # Create a customer profile
        self.customer = Customer.objects.create(user_id=self.customer_user.id, first_name='John', last_name='Doe', email='customer@example.com')

        # Create past and present orders for the customer
        self.past_order = Order.objects.create(
            order_number='123',
            height=10,
            width=10,
            length=10,
            package_weight=5,
            pickup_or_dropoff='Pickup',
            pickup_address='123 Main St',
            delivery_address='456 Elm St',
            shipping_type='Standard',
            estimated_cost=50.00,
            status='Delivered',
            customer=self.customer
        )
        self.present_order = Order.objects.create(
            order_number='456',
            height=15,
            width=15,
            length=15,
            package_weight=10,
            pickup_or_dropoff='Dropoff',
            pickup_address='789 Oak St',
            delivery_address='987 Maple St',
            shipping_type='Express',
            estimated_cost=75.00,
            status='Processing',
            customer=self.customer
        )

    def test_customer_can_see_orders(self):
        # Log in as the customer
        self.client.login(username='customer', password='password123')
        # Set the user type in the session
        session = self.client.session
        session['user_type'] = 'customer'
        session.save()

        # Retrieve the customer's orders page
        response = self.client.get(reverse('customer-dashboard'))

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that past and present orders are displayed
        self.assertContains(response, self.past_order.order_number)
        self.assertContains(response, self.present_order.order_number)
        
class ProfileUpdateTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.test_user = User.objects.create_user(username='testuser', password='password123')

        # Create a customer profile for the test user
        self.customer_profile = Customer.objects.create(
            user_id=self.test_user.id,
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            address='123 Main St',
            phone='123-456-7890'
        )

        # Log the test user in
        self.client.login(username='testuser', password='password123')

    def test_profile_update(self):
        # Define new valid profile information
        new_first_name = 'Jane'
        new_last_name = 'Smith'
        new_address = '456 Elm St'
        new_phone = '987-654-3210'

        # Send POST request to update profile
        response = self.client.post(reverse('customer-profile'), {
            'first_name': new_first_name,
            'last_name': new_last_name,
            'address': new_address,
            'phone': new_phone
        })

        # Check if the profile was updated successfully
        self.assertEqual(response.status_code, 200)

        # Refresh the customer profile from the database
        self.customer_profile.refresh_from_db()

        # Check if the profile information matches the updated values
        self.assertEqual(self.customer_profile.first_name, new_first_name)
        self.assertEqual(self.customer_profile.last_name, new_last_name)
        self.assertEqual(self.customer_profile.address, new_address)
        self.assertEqual(self.customer_profile.phone, new_phone)
        
class ProfileUpdateInvalidTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.test_user = User.objects.create_user(username='testuser', password='password123')

        # Create a customer profile for the test user
        self.customer_profile = Customer.objects.create(
            user_id=self.test_user.id,
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            address='123 Main St',
            phone='123-456-7890'
        )

        # Log the test user in
        self.client.login(username='testuser', password='password123')

    def test_profile_update_invalid(self):
        # Attempt to update profile with invalid information (e.g., empty first name)
        response = self.client.post(reverse('customer-profile'), {
            'first_name': '',  # Invalid: Empty first name
            'last_name': 'Smith',
            'address': '456 Elm St',
            'phone': '987-654-3210'
        })

        # Check if the profile was not updated (expecting form validation errors)
        self.assertEqual(response.status_code, 200)  # Assuming the view returns HTTP 200 on form validation failure
        # Make a GET request to refresh the customer profile page
        response = self.client.get(reverse('customer-profile'))
        # Refresh the customer profile from the database
        self.customer_profile.refresh_from_db()

        # Check if the profile information remains unchanged
        self.assertEqual(self.customer_profile.first_name, 'John')
        self.assertEqual(self.customer_profile.last_name, 'Doe')
        self.assertEqual(self.customer_profile.address, '123 Main St')
        self.assertEqual(self.customer_profile.phone, '123-456-7890')

class ValidOrderPlacementTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer_email = "customer@example.com"
        self.customer_password = "Password123!"
        # Create a customer user
        self.customer_user = User.objects.create_user(username=self.customer_email, email=self.customer_email, password=self.customer_password)
        # Create a customer profile
        self.customer_profile = Customer.objects.create(user_id=self.customer_user.id, first_name='John', last_name='Doe', email=self.customer_email)

    def test_place_valid_order(self):
        # Log in the customer user
        self.client.login(username=self.customer_email, password=self.customer_password)

        # Simulate a POST request to place a new order
        new_order_data = {
            'height': 10.0,
            'width': 10.0,
            'length': 10.0,
            'package_weight': 10.0,
            'pickup_or_dropoff': 'pickup',
            'pickup_address': '123 Main St, Anytown, NY 12345',
            'delivery_address': '123 Main St, Anytown, NY 12345',
            'shipping_type': 'ground',
        }
        response = self.client.post(reverse('place-order'), new_order_data)
        
        # Check if the order has been successfully placed
        self.assertEqual(response.status_code, 302)  # Expecting redirect after successful order placement
        
        # Check if the order is associated with the correct customer
        self.assertTrue(Order.objects.filter(customer=self.customer_profile).exists())
        
class InvalidOrderPlacementTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer_email = "customer@example.com"
        self.customer_password = "Password123!"
        self.customer_user = User.objects.create_user(username=self.customer_email, email=self.customer_email, password=self.customer_password)
        self.customer_profile = Customer.objects.create(user_id=self.customer_user.id, first_name='John', last_name='Doe', email=self.customer_email)

    def test_place_invalid_order_missing_data(self):
        self.client.login(username=self.customer_email, password=self.customer_password)
        invalid_order_data = {}  # Missing required data
        response = self.client.post(reverse('place-order'), invalid_order_data)
        # Check that order was not created
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.exists())  # Ensure no order was created

    def test_place_invalid_order_invalid_weight(self):
        self.client.login(username=self.customer_email, password=self.customer_password)
        invalid_order_data = {'package_weight': -5.0}  # Invalid weight
        response = self.client.post(reverse('place-order'), invalid_order_data)
        # Check that order was not created
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.exists())  # Ensure no order was created

class ShippingAddressTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer_email = "customer@example.com"
        self.customer_password = "Password123!"
        # Create a customer user
        self.customer_user = User.objects.create_user(username=self.customer_email, email=self.customer_email, password=self.customer_password)
        # Create a customer profile
        self.customer_profile = Customer.objects.create(user_id=self.customer_user.id, first_name='John', last_name='Doe', email=self.customer_email)

    def test_place_valid_order(self):
        # Log in the customer user
        self.client.login(username=self.customer_email, password=self.customer_password)

        # Simulate a POST request to place a new order without shipping address
        new_order_data = {
            'height': 10.0,
            'width': 10.0,
            'length': 10.0,
            'package_weight': 10.0,
            'pickup_or_dropoff': 'pickup',
            'pickup_address': '123 Main St, Anytown, NY 12345',
            'delivery_address': '123 Main St, Anytown, NY 12345',
            'shipping_type': 'ground',
        }
        response = self.client.post(reverse('place-order'), new_order_data)
        
        # Check if the order has been successfully placed
        self.assertEqual(response.status_code, 302)  # Expecting redirect after successful order placement
        
        # Check if the order is associated with the correct customer
        self.assertTrue(Order.objects.filter(customer=self.customer_profile).exists())
        
        # Update the order object with shipping address info
        order = Order.objects.get(customer=self.customer_profile)
        order.delivery_address = '123 Main St, Anytown, NY 12345'
        order.save()
        
        # Check if the shipping address info is correctly updated
        self.assertEqual(order.delivery_address, '123 Main St, Anytown, NY 12345')
            
class InvalidShippingAddressTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer_email = "customer@example.com"
        self.customer_password = "Password123!"
        # Create a customer user
        self.customer_user = User.objects.create_user(username=self.customer_email, email=self.customer_email, password=self.customer_password)
        # Create a customer profile
        self.customer_profile = Customer.objects.create(user_id=self.customer_user.id, first_name='John', last_name='Doe', email=self.customer_email)

    def test_invalid_shipping_address(self):
        # Log in the customer user
        self.client.login(username=self.customer_email, password=self.customer_password)

        # Simulate a POST request to provide an invalid shipping address
        invalid_shipping_address_data = {
            'height': 10.0,
            'width': 10.0,
            'length': 10.0,
            'package_weight': 10.0,
            'pickup_or_dropoff': 'pickup',
            'pickup_address': '',  # Invalid address (empty string)
            'delivery_address': '', # Invalid address (empty string)
            # Add other required fields as needed
        }
        response = self.client.post(reverse('place-order'), invalid_shipping_address_data)
        
        # Check if the response indicates that the order was not placed
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.exists())  # Ensure no order was created
        

