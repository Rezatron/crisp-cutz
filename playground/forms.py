import requests
import json
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Barber, Customer, Availability, Appointment, Haircut
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, get_user_model

from django.core.exceptions import ValidationError

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
            response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyD3Bk4vpGUe1hsJf6qbzfUHUtmrB6nIL5E'.format(location))
            print("Response status code:", response.status_code)
            response_json = response.json()
            print("Response JSON:", response_json)
            if response.status_code != 200 or response_json['status'] != 'OK':
                if 'error_message' in response_json:
                    print("Error message:", response_json['error_message'])
                raise ValidationError("Invalid location")
            # Extract the formatted address from the geocode result
            formatted_address = response_json['results'][0]['formatted_address']
            # Extract the latitude and longitude from the geocode result
            lat = response_json['results'][0]['geometry']['location']['lat']
            lng = response_json['results'][0]['geometry']['location']['lng']
            # Store the latitude and longitude in the Barber model
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
            response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyD3Bk4vpGUe1hsJf6qbzfUHUtmrB6nIL5E'.format(location))
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
            response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyD3Bk4vpGUe1hsJf6qbzfUHUtmrB6nIL5E'.format(location))
            print("Response status code:", response.status_code)
            response_json = response.json()
            print("Response JSON:", response_json)
            if response.status_code != 200 or response_json['status'] != 'OK':
                if 'error_message' in response_json:
                    print("Error message:", response_json['error_message'])
                raise ValidationError("Invalid location")
            # Extract the formatted address from the geocode result
            formatted_address = response_json['results'][0]['formatted_address']
            # Extract the latitude and longitude from the geocode result
            lat = response_json['results'][0]['geometry']['location']['lat']
            lng = response_json['results'][0]['geometry']['location']['lng']
            # Store the latitude and longitude in the Customer model
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
            response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyD3Bk4vpGUe1hsJf6qbzfUHUtmrB6nIL5E'.format(location))
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
        fields = ['barber', 'haircut', 'date_time']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['barber'].queryset = Barber.objects.filter(is_available=True)
        self.fields['haircut'].queryset = Haircut.objects.all()