import requests
import json
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Barber, Customer, Availability, Appointment, Service, AppointmentService
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, get_user_model
from .utils import is_barber_available
from django.core.exceptions import ValidationError
from .views.common_views import address_to_coordinates
from django.conf import settings
class BarberRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    bio = forms.CharField(max_length=500, required=True)
    profile_picture = forms.ImageField(required=False)
    experience_years = forms.IntegerField(required=True)
    is_available = forms.BooleanField(required=False)
    service_menu = forms.CharField(widget=forms.Textarea, required=False)
    booking_preferences = forms.CharField(widget=forms.Textarea, required=False)
    location = forms.CharField(max_length=100, required=True)
    specialization = forms.CharField(max_length=100, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = Barber
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'bio', 'profile_picture', 'experience_years', 'is_available', 'service_menu', 'booking_preferences', 'location', 'specialization']

    def clean_location(self):
        location = self.cleaned_data.get('location')
        if location:
            response = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={settings.GOOGLE_MAPS_API_KEY}')
            response_json = response.json()
            if response.status_code != 200 or response_json['status'] != 'OK':
                raise ValidationError("Invalid location")
            formatted_address = response_json['results'][0]['formatted_address']
            lat = response_json['results'][0]['geometry']['location']['lat']
            lng = response_json['results'][0]['geometry']['location']['lng']
            self.instance.latitude = lat
            self.instance.longitude = lng
            return formatted_address
        return location

class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    location = forms.CharField(max_length=100, required=True)

    class Meta:
        model = Customer
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone_number', 'location']

    def clean_location(self):
        location = self.cleaned_data.get('location')
        if location:
            response = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={settings.GOOGLE_MAPS_API_KEY}')
            response_json = response.json()
            if response.status_code != 200 or response_json['status'] != 'OK':
                raise ValidationError("Invalid location")
            formatted_address = response_json['results'][0]['formatted_address']
            return formatted_address
        return location

class CustomerLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)

        if not user or not user.check_password(password):
            raise forms.ValidationError("Incorrect username or password")

        return super(CustomerLoginForm, self).clean()

class BarberLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)

        if not user or not user.check_password(password):
            raise forms.ValidationError("Incorrect username or password")

        return super(BarberLoginForm, self).clean()

class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['start_time', 'end_time', 'is_available']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class CustomerUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    location = forms.CharField(max_length=100, required=True)

    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'location']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'location' not in self.data and self.instance and self.instance.pk:
            self.data = self.data.copy()
            self.data['location'] = self.instance.location

    def clean_location(self):
        location = self.cleaned_data.get('location')
        if location:
            response = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={settings.GOOGLE_MAPS_API_KEY}')
            response_json = response.json()
            if response.status_code != 200 or response_json['status'] != 'OK':
                raise ValidationError("Invalid location")
            formatted_address = response_json['results'][0]['formatted_address']
            lat = response_json['results'][0]['geometry']['location']['lat']
            lng = response_json['results'][0]['geometry']['location']['lng']
            self.instance.latitude = lat
            self.instance.longitude = lng
            return formatted_address
        return location

class BarberUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    location = forms.CharField(max_length=100, required=True)

    class Meta:
        model = Barber
        fields = ['first_name', 'last_name', 'email', 'bio', 'profile_picture', 'experience_years', 'is_available', 'service_menu', 'booking_preferences', 'location', 'specialization']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'location' not in self.data and self.instance and self.instance.pk:
            self.data = self.data.copy()
            self.data['location'] = self.instance.location

    def clean_location(self):
        location = self.cleaned_data.get('location')
        if location:
            response = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={settings.GOOGLE_MAPS_API_KEY}')
            response_json = response.json()
            if response.status_code != 200 or response_json['status'] != 'OK':
                raise ValidationError("Invalid location")
            formatted_address = response_json['results'][0]['formatted_address']
            lat = response_json['results'][0]['geometry']['location']['lat']
            lng = response_json['results'][0]['geometry']['location']['lng']
            self.instance.latitude = lat
            self.instance.longitude = lng
            return formatted_address
        return location

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['barber', 'services', 'date_time']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['barber'].queryset = Barber.objects.filter(is_available=True)
        self.fields['services'].queryset = Service.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        barber = cleaned_data.get('barber')
        services = cleaned_data.get('services')
        date_time = cleaned_data.get('date_time')

        if not barber or not services or not date_time:
            return cleaned_data

        # Calculate end_time based on services
        total_duration = sum(service.duration for service in services)
        end_time = date_time + total_duration

        # Check barber availability
        if not is_barber_available(barber, date_time, end_time):
            self.add_error(None, 'The barber is not available at this time.')

        cleaned_data['end_time'] = end_time
        return cleaned_data

    def save(self, commit=True):
        appointment = super().save(commit=False)
        appointment.end_time = self.cleaned_data['end_time']
        
        if commit:
            appointment.save()
            self.save_m2m()  # Save the many-to-many relationship
        return appointment