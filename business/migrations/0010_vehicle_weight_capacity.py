# Generated by Django 4.1 on 2024-04-08 02:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "business",
            "0009_remove_driver_vehicle_remove_package_is_processing_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="vehicle",
            name="weight_capacity",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
    ]