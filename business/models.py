from django.db import models
from customer.models import Customer
from django.utils import timezone


class Package(models.Model):
    package_id = models.AutoField(primary_key=True)
    shipment = models.ForeignKey('Shipment', on_delete=models.SET_NULL, null=True, blank=True)
    package_description = models.TextField(null=True, blank=True)
    package_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    package_dimensions = models.CharField(max_length=255, null=True, blank=True)
    package_status = models.CharField(max_length=50, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    package_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')

class Shipment(models.Model):
    id = models.AutoField(primary_key=True)
    order_number = models.CharField(max_length=50, null=True, blank=True)
    customer_id = models.IntegerField(null=True, blank=True)
    order_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    shipment_date = models.DateField(null=True, blank=True)
    driver_id = models.IntegerField(null=True, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Vehicle(models.Model):
    vehicle_id = models.AutoField(primary_key=True)
    vehicle_model = models.CharField(max_length=100, null=True, blank=True)
    vehicle_plate = models.CharField(max_length=20, null=True, blank=True)
    vehicle_status = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return f"{self.vehicle_model} - {self.vehicle_plate}"

class Driver(models.Model):
    driver_id = models.AutoField(primary_key=True)
    driver_name = models.CharField(max_length=100, null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='drivers', default=1)

    def __str__(self):
        return self.driver_name