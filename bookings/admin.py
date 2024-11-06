from django.contrib import admin
from .models import Booking, CustomUser

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'last_name', 'first_name', 'phone_number', 'username')
    search_fields =('email',)
    fields = ('email', 'last_name', 'first_name', 'phone_number', 'username')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('starting_city','destination_city', 'name', 'email', 'created_at')
    search_fields = ('name',)
    fields = ('start', 'destination', 'name', 'travel_date', 'created_at')