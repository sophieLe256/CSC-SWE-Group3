# Generated by Django 5.0.3 on 2024-04-09 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0005_customer_notification_preference'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
    ]
