# Generated by Django 5.0.1 on 2024-01-17 23:25

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('driver_management', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_number', models.CharField(max_length=10, unique=True)),
                ('customer_name', models.CharField(max_length=60)),
                ('pickup_location', models.CharField(max_length=255)),
                ('drop_off_location', models.CharField(max_length=255)),
                ('departure_time', models.DateTimeField()),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('Processing', 'Processing'), ('In Transit', 'In Transit'), ('Delivered', 'Delivered')], default='Processing', max_length=20)),
                ('vehicle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='driver_management.vehicle')),
            ],
        ),
    ]