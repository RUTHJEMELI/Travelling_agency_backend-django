# Generated by Django 5.1.2 on 2024-10-16 12:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0003_rename_destination_booking_destination_city_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='travel_date',
        ),
    ]
