from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
     user_registration_view,
     login_view,
     create_appointment_view,
     
)



urlpatterns = [
    path('api/token/', login_view, name='login'),
    path('api/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('users/register/', user_registration_view, name='register'),

    path('booking/', create_appointment_view, name='book'),

]
