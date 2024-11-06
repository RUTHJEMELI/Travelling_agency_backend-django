from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('booking/', include('bookings.urls')),  # Include the app's URLs here
    # Add other app URLs if needed
]
