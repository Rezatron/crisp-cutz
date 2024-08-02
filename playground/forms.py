import requests
import json
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Barber, Customer, Availability, Appointment, Service, AppointmentService, BarberService
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, get_user_model
from .utils import is_barber_available
from django.core.exceptions import ValidationError
from .views.common_views import address_to_coordinates
from django.conf import settings
from playground.models import BarberService
from datetime import timedelta
from django.forms import modelformset_factory


BarberServiceFormSet = modelformset_factory(
    BarberService,
    fields=['service', 'price', 'duration'],
    extra=1,
    can_delete=True
)

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
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.none(),  # Default to none to be populated later
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Appointment
        fields = ['barber', 'services', 'date_time']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        initial_barber_id = kwargs.get('initial', {}).get('barber')
        super().__init__(*args, **kwargs)

        # Set queryset for barber field
        self.fields['barber'].queryset = Barber.objects.filter(is_available=True)

        # Set queryset for services field based on initial barber
        if initial_barber_id:
            self.fields['services'].queryset = Service.objects.filter(
                barberservice__barber_id=initial_barber_id
            ).distinct()
        elif self.instance and self.instance.pk and hasattr(self.instance, 'barber'):
            self.fields['services'].queryset = Service.objects.filter(
                barberservice__barber_id=self.instance.barber.id
            ).distinct()

class BarberServiceForm(forms.ModelForm):
    class Meta:
        model = BarberService
        fields = ['service', 'price', 'duration']
        widgets = {
            'duration': forms.TextInput(attrs={'type': 'text', 'placeholder': 'Duration in HH:MM:SS'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate the service field with all existing Service instances
        self.fields['service'].queryset = Service.objects.all()
    
    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        duration = cleaned_data.get('duration')

        if price is not None and price <= 0:
            self.add_error('price', 'Price must be greater than 0.')

        if duration:
            try:
                duration_obj = timedelta(hours=int(duration.split(':')[0]), minutes=int(duration.split(':')[1]), seconds=int(duration.split(':')[2]))
                if duration_obj <= timedelta():
                    self.add_error('duration', 'Duration must be greater than 0.')
            except (ValueError, IndexError):
                self.add_error('duration', 'Invalid duration format. Use HH:MM:SS.')

        return cleaned_data

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'price', 'duration']
        widgets = {
            'duration': forms.TextInput(attrs={'type': 'text', 'placeholder': 'Duration in HH:MM:SS'}),
        }