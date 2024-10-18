from django.db import models
from django.core.validators import RegexValidator

from .managers import CustomUsermanager
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext as _ 


# Create your models here.
class CustomUser(AbstractBaseUser):
    email = models.EmailField(max_length=30, blank=False, unique=True, verbose_name=_('email'))
    first_name = models.CharField(max_length=20, blank=False, verbose_name=_('firstName'))
    last_name = models.CharField(max_length=20, blank=False, verbose_name=_('lastName'))
    username = models.CharField(max_length=20, blank=False, verbose_name=_('username'))
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    profile = models.ImageField(
        upload_to='profiles/',
        default= 'profiles/default.jpg',
        blank=True,
        verbose_name=_('profilePic')
    )

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )


    phone_number = models.CharField(max_length=20,validators=[phone_regex], blank=False, verbose_name=_('phone number'))



    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name', 'last_name']


    objects = CustomUsermanager()



    def __str__(self):
        return self.username



class Booking(models.Model):
    
    destination_city = models.CharField(max_length=25, blank=False, verbose_name=_('To'))
    starting_city = models.CharField(max_length=25, blank=False, verbose_name=_('From'))
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings', verbose_name=_('Client'), blank=False)
    created_at = models.DateField(auto_now_add=True)
    isComplete = models.BooleanField(default=False)



    def __str__(self):
        return self.destination
