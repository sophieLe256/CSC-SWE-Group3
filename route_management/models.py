import uuid
import json
from django.db import models

class Route(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30)
    origin = models.CharField(max_length=100)
    distance_miles = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    destination = models.CharField(max_length=100, default='')
    updated_at = models.DateTimeField(auto_now=True)
    
    stops = models.TextField() 
    arrival_times = models.TextField()
    departure_times = models.TextField()

    orders = models.ManyToManyField('order_management.Order')
    
    def save(self, *args, **kwargs):
        if isinstance(self.stops, list):
            self.stops = json.dumps(self.stops)
        if isinstance(self.arrival_times, list):
            self.arrival_times = json.dumps(self.arrival_times)
        if isinstance(self.departure_times, list):
            self.departure_times = json.dumps(self.departure_times)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} route"
