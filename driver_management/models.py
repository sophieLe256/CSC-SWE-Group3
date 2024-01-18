from django.db import models


class Driver(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30) 
    employee_id = models.CharField(max_length=10, unique=True)
    phone_number = models.CharField(max_length=20)
    driver_license = models.CharField(max_length=50) 
    work_permit = models.ImageField(upload_to='work_permits/')
    salary = models.DecimalField(max_digits=8, decimal_places=2)
    schedule = models.TextField()
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Vehicle(models.Model):
    license_plate = models.CharField(max_length=10, unique=True)
    model = models.CharField(max_length=30) 
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)