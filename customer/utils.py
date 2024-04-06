from django.db import transaction
from .models import Customer, Admin, Package, Shipment, Order, Feedback

def wipe_database():
    with transaction.atomic():
        Customer.objects.all().delete()
        Admin.objects.all().delete()
        Package.objects.all().delete()
        Shipment.objects.all().delete()
        Order.objects.all().delete()
        Feedback.objects.all().delete()
        