# Generated by Django 5.0.3 on 2024-04-07 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0005_package_vehicle_vehicle_available_space_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='is_processing',
            field=models.BooleanField(default=True),
        ),
    ]
