from django.shortcuts import render

from django.views.generic import ListView 
from .models import Driver

class DriverListView(ListView):
  model = Driver
  context_object_name = 'drivers'