from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate

from .models import Booking, CustomUser
from .serializers import (
    CustomUserSerializer, BookingSerializer, LoginSerializer, 
    TokenObtainPairSerializer
)
from .utils import get_all_cities


# User Registration
class UserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.save()
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            response = Response({
                'user': CustomUserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)

            response.set_cookie('refresh_token', str(refresh), httponly=True)
            response.set_cookie('access_token', str(refresh.access_token), httponly=True)
            return response
        
        # Return custom error message if registration fails
        return Response({'error': 'Registration failed.'}, status=status.HTTP_400_BAD_REQUEST)
    

user_registration_view = UserRegistrationView.as_view()


# Login View with Custom Error Message
class LoginView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            
            user = authenticate(request, email=email, password=password)
            if user:
                # Generate tokens if authentication is successful
                refresh = RefreshToken.for_user(user)
                response = Response({
                    'user': CustomUserSerializer(user).data,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'message': 'Login successful'
                }, status=status.HTTP_200_OK)

                # Set cookies
                response.set_cookie('refresh_token', str(refresh), httponly=True)
                response.set_cookie('access_token', str(refresh.access_token), httponly=True)
                return response
            
            # Return custom error message if authentication fails
            return Response({'error': 'Incorrect email or password.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Return error if serializer is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
login_view = LoginView.as_view()


# Logout View
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        response = Response({'message': 'Successfully logged out'}, status=status.HTTP_205_RESET_CONTENT)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

logout_view = LogoutView.as_view()


# Create and List Appointments
class CreateAppointmentView(generics.ListCreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [AllowAny]


    def create(self, request, *args, **kwargs):
        # Prevent multiple incomplete bookings
        

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        

        # Send email notification to admin
        subject = f"New Appointment by {request.data.get('name')}"
        message = (
            f"Name: {request.data.get('name')}\n"
            f"Email: {request.data.get('email')}\n"


            f"Phone number: {request.data.get('phone_number')}\n\n"
            f"Destination: {request.data.get('destination_city')}\n\n"
            f"From: {request.data.get('starting_city')}\n\n"
            f"Ticket No: {booking.id}"
        )
        send_mail(
            subject, message, settings.DEFAULT_FROM_EMAIL,
            ['info@opendoorstravelling.com'], fail_silently=False
        )
        
        return Response({'message': 'Appointment booked successfully'}, status=status.HTTP_201_CREATED)

    # def get(self, request, *args, **kwargs):
    #     my_bookings = self.queryset.filter(client=request.user)
    #     serializer = self.get_serializer(my_bookings, many=True)
        
    #     if my_bookings.exists():
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response({'message': 'No appointments found.'}, status=status.HTTP_204_NO_CONTENT)

create_appointment_view = CreateAppointmentView.as_view()


# Dashboard View for Admin
# class DashboardView(generics.GenericAPIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         all_appointments = Booking.objects.all()
#         incomplete_appointments = Booking.objects.filter(isComplete=False)

#         return Response({
#             'all_appointments': BookingSerializer(all_appointments, many=True).data,
#             'incomplete_appointments': BookingCompletedSerializer(incomplete_appointments, many=True).data,
#         }, status=status.HTTP_200_OK)

#     def post(self, request, *args, **kwargs):
#         appointment_id = request.data.get('booking_id')
#         appointment = get_object_or_404(Booking, id=appointment_id)
        
#         if not appointment.isComplete:
#             serializer = BookingCompletedSerializer(appointment, data={'isComplete': True}, partial=True)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return Response({'message': 'Appointment marked as complete.'}, status=status.HTTP_200_OK)
        
#         return Response({'message': 'Appointment is already complete.'}, status=status.HTTP_400_BAD_REQUEST)

# dashboard_view = DashboardView.as_view()


# Delete Appointment
class DeleteAppointment(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id, client=request.user)

        if booking.isComplete:
            return Response({'message': 'Cannot delete completed appointments.'}, status=status.HTTP_400_BAD_REQUEST)

        time_difference = timezone.now() - booking.created_at
        if time_difference.total_seconds() <= 3600:
            booking.delete()
            return Response({'message': 'Appointment deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        
        return Response({'message': 'Cannot delete an appointment after one hour of booking.'}, status=status.HTTP_400_BAD_REQUEST)

delete_appointment_view = DeleteAppointment.as_view()


# Get List of Cities
class CitiesListView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        cities = get_all_cities()
        if cities:
            return Response(cities, status=status.HTTP_200_OK)
        return Response({'error': 'Could not fetch cities'}, status=status.HTTP_400_BAD_REQUEST)

list_of_cities = CitiesListView.as_view()
