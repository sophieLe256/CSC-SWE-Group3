import folium
from django.shortcuts import render
from customer.models import Order
from django.core.exceptions import ObjectDoesNotExist

def package_status(request):
    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number')
        try:
            order = Order.objects.get(order_number=tracking_number)
            # Create a Folium map centered on Atlanta
            m = folium.Map(location=[33.7490, -84.3880], zoom_start=12)
            # Add a marker at the pickup address
            folium.Marker([33.7490, -84.3880], popup="Pickup Address").add_to(m)
            # Add a marker at the delivery address
            folium.Marker([33.7490, -84.3880], popup="Delivery Address").add_to(m)
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