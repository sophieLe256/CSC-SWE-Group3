from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Sends a test email'

    def handle(self, *args, **options):
        subject = 'Test Email'
        message = 'This is a test email.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = ['test_email@gmail.com']  # Replace with the desired test email address
        send_mail(subject, message, from_email, recipient_list)
        self.stdout.write(self.style.SUCCESS('Test email sent'))
