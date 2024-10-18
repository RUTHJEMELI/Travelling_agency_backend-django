from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.mail import send_mail 
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView

from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Booking, CustomUser
from  .serializers import CustomUserSerializer, BookingSerializer, LoginSerializer, TokenObtainPairSerializer
from .utils import get_all_cities


# Create your views here.
# register user
# login
# update, delete, book, view a flight
# dashboard all the flights

# every successful book delete and update the admin should get an email with details of the user

#bonus a ticket is given on book and cancelled on delete/cancel 

# User Registration

class UserRegistration(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]



    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request':request})

        serializer.is_valid(raise_exception = True)

        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': CustomUserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    


user_registration_view = UserRegistration.as_view()



#     # user login
# class UserLogin(generics.GenericAPIView):
#     serializer_class = LoginSerializer
#     permission_classes =[AllowAny]


#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data)


#         serializer.is_valid(raise_exception=True)


#         email = serializer.validated_data['email']
#         password = serializer.validated_data['password']


#         user = authenticate(email=email, password=password)



#         if not user:
#             return Response('The user credentials are wrong', status=status.HTTP_400_BAD_REQUEST)
        


#         token, created = Token.objects.get_or_create(user=user)


#         return Response({
#             'token':token.key,
#             'user':CustomUserSerializer(user).data
#         }, status=status.HTTP_200_OK)
    
# user_login_view = UserLogin.as_view()

class LoginView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request':request})


        serializer.is_valid(raise_exception = True)



        response = Response(serializer.data, status=status.HTTP_200_OK)

        response.set_cookie(key='refresh_token',value=serializer.validated_data['refresh'], httponly=True)
        response.set_cookie(key='access_token', value=serializer.validated_data['access'], httponly=True)

        return response


login_view = LoginView.as_view()


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]


class CreateAppointmentView(generics.ListCreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]


    def create(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception = True)


        booking = serializer.save(client=request.user )


        user = request.user
        destination = request.data.get('destination_city')
        starting_from = request.data.get('starting_city')
        phone_number = request.data.get('phone_number')


        subject = f"New Appointment by {user}"
        message = (
            f"User: {user}\n"
            f"Phone_number: {phone_number}\n"
            f"Destination: {destination}\n"
            f"From: {starting_from}\n"
            f"Booking ID: {booking.id}"
        )


        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            ['mutaikiptanui@gmail.com'],
            fail_silently=False

        )
        



        return Response({'message':'appointment booked successfully'}, status=status.HTTP_201_CREATED)

    


    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        myBookings = queryset.filter(client = self.request.user)

        if myBookings.exists():
            serializer = self.get_serializer(myBookings, many=True)
        else:
            return Response('No appointments made', status=status.HTTP_204_NO_CONTENT)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
create_appointment_appointments_view = CreateAppointmentView.as_view()
    

class CitiesListView(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        cities = get_all_cities()
        if cities:
            return Response(cities, status=status.HTTP_200_OK)
        return Response({'error':'could not fetch cities'}, status=status.HTTP_400_BAD_REQUEST)
    
list_of_cities = CitiesListView.as_view()






