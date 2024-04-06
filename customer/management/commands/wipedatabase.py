from django.core.management.base import BaseCommand
from customer.utils import wipe_database

class Command(BaseCommand):
    help = 'Wipes the entire database without removing tables'

    def handle(self, *args, **options):
        wipe_database()
        self.stdout.write(self.style.SUCCESS('Database wiped successfully.'))
