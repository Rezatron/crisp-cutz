from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Barber, Customer

class BarberRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = Barber
        fields = ['username', 'email', 'password1',  'bio', 'profile_picture', 'experience_years', 'is_available', 'service_menu', 'booking_preferences', 'location', 'specialization']


class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = Customer
        fields = ['username', 'email', 'password1', 'phone_number', 'notification_preferences', 'address']