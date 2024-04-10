import folium
from django.shortcuts import render
from customer.models import Order
from django.core.exceptions import ObjectDoesNotExist
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError 

def package_status(request):
    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number')
        try:
            order = Order.objects.get(order_number=tracking_number)
            
            pickup_latitude, pickup_longitude = get_coordinates(order.pickup_address)
            delivery_latitude, delivery_longitude = get_coordinates(order.delivery_address)
            
            # Create a Folium map centered on Atlanta
            m = folium.Map(location=[33.7490, -84.3880], zoom_start=12)
            # Add a marker at the pickup address
            folium.Marker([pickup_latitude, pickup_longitude], popup="Pickup Address").add_to(m)
            # Add a marker at the delivery address
            folium.Marker([delivery_latitude, delivery_longitude], popup="Delivery Address").add_to(m)
            
            map_html = m._repr_html_()
            context = {
                'order': order,
                'map_html': map_html
            }
            return render(request, 'tracking/package_status.html', context)
        except ObjectDoesNotExist:
            context = {
                'error': 'Invalid tracking number.'
            }
            return render(request, 'tracking/package_status.html', context)
    return render(request, 'tracking/package_status.html')


def get_coordinates(location):
    # Check if the location contains a comma, indicating it's likely a partial address with a zip code
    if "," in location:
        address = location
    else:
        # Assume it's a partial address with a zip code
        address = f"{location.split(',')[0].strip()}, USA"  # Extract the street and append with default city and state
    
    geolocator = Nominatim(user_agent="geopy_explorer")

    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        else:
            return 33.7490, -84.3880  # Default fallback coordinates
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"Geocoding failed: {e}")
        # Return default fallback coordinates
        return 33.7490, -84.3880  # Default fallback coordinates