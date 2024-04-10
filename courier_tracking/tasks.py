from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Customer

@shared_task
def send_verification_email(customer_id):
    customer = Customer.objects.get(id=customer_id)
    subject = 'Verify Your Email'
    html_message = render_to_string('customer/verification_email.html', {'customer': customer})
    plain_message = strip_tags(html_message)
    from_email = 'couriertracking01@gmail.com'  # Replace with your Gmail email address
    to_email = customer.email
    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
