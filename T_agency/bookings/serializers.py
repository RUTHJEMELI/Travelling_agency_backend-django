from rest_framework import serializers
from rest_framework_simplejwt.serializers import  TokenObtainPairSerializer
from django.contrib.auth import authenticate

from .models import Booking, CustomUser




class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only =True)
    confirm_password = serializers.CharField(write_only = True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'phone_number', 'password', 'confirm_password','username','first_name', 'last_name']


    def validate(self, attrs):
        
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError('password mismatch')
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')

        user = CustomUser(
            email = validated_data['email'],
            username = validated_data['username'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            phone_number = validated_data['phone_number']
        )

        user.set_password(validated_data['password'])

        user.save()

        return user
    



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only = True)


class BookingSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField( read_only =True)
    created_at = serializers.DateTimeField(read_only =True)
    isComplete = serializers.BooleanField(read_only = True)

    class Meta:
        model = Booking
        fields = ['destination_city','starting_city', 'client', 'created_at', 'isComplete']


    
    




class TokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    # adding email to the payload
    def get_user(cls, user):
        token = super().get_user(user)
        
        token['email'] = user.email

        return token
    
    def validate(self, attrs): 

        email = attrs.get('email')
        password = attrs.get('password')
        try:
            user = CustomUser.objects.get(email = email)

        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('user with such email does not exist!')
        
        authenticatedUser = authenticate(request=self.context.get('request'), email=user.email, password=password)

        if not authenticatedUser:
            raise serializers.ValidationError('incorrect credentials')
        
        data = super().validate(attrs)
 
        return data