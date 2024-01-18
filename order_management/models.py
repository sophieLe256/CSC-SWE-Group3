from django.db import models
import uuid

class Order(models.Model):
    order_number = models.CharField(max_length=10, unique=True) 
    customer_name = models.CharField(max_length=60)
    pickup_location = models.CharField(max_length=255)
    drop_off_location = models.CharField(max_length=255)
    departure_time = models.DateTimeField()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    vehicle = models.ForeignKey('driver_management.Vehicle', on_delete=models.SET_NULL, blank=True, null=True)

    STATUS_CHOICES = [
        ('Processing', 'Processing'),
        ('In Transit', 'In Transit'),
        ('Delivered', 'Delivered')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Processing')

    def __str__(self):
        return f"Order {self.order_number} is {self.status}. Pickup at {self.departure_time}"