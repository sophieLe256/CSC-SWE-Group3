from django.db import models
from customer.models import Customer
from django.utils import timezone


class Shipment(models.Model):
    tracking_number = models.CharField(max_length=20, unique=True)
    package_description = models.TextField(null=True, blank=True)
    pickup_address = models.CharField(max_length=255)
    delivery_address = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='Processing')
    updated_at = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)