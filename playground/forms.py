import requests
import json
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Barber, Customer, Availability, Appointment, Service, AppointmentService, BarberService
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, get_user_model

from django.core.exceptions import ValidationError
from .views.common_views import address_to_coordinates
from django.conf import settings
from playground.models import BarberService
from datetime import datetime, timedelta, time

from django.forms import modelformset_factory
from django import forms
from .models import Appointment, Barber, Service


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
    barber = forms.ModelChoiceField(
        queryset=Barber.objects.all(),  # Default queryset
        required=True
    )
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),  # Default queryset
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

        if initial_barber_id:
            self.fields['barber'].queryset = Barber.objects.filter(id=initial_barber_id)
            self.fields['barber'].initial = initial_barber_id

            self.fields['services'].queryset = Service.objects.filter(
                barberservice__barber_id=initial_barber_id
            ).distinct()
        else:
            self.fields['barber'].queryset = Barber.objects.filter(is_available=True)
            self.fields['services'].queryset = Service.objects.none()




class BarberServiceForm(forms.ModelForm):
    class Meta:
        model = BarberService
        fields = ['price', 'duration']

    def clean(self):
        cleaned_data = super().clean()
        duration = cleaned_data.get('duration')

        if isinstance(duration, str):
            # Assuming the duration is provided as a string in HH:MM:SS format
            try:
                duration_obj = timedelta(
                    hours=int(duration.split(':')[0]),
                    minutes=int(duration.split(':')[1]),
                    seconds=int(duration.split(':')[2])
                )
            except (ValueError, IndexError):
                raise forms.ValidationError("Invalid duration format. It should be HH:MM:SS.")
        elif isinstance(duration, timedelta):
            # If the duration is already a timedelta object
            duration_obj = duration
        else:
            raise forms.ValidationError("Invalid duration format.")

        # Set the cleaned duration back to cleaned_data
        cleaned_data['duration'] = duration_obj
        return cleaned_data


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'price', 'duration']
        widgets = {
            'duration': forms.TextInput(attrs={'type': 'text', 'placeholder': 'Duration in HH:MM:SS'}),
        }







class ReviewForm(forms.Form):
    overall_experience = forms.FloatField(
        min_value=0.5,
        max_value=5.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rate your overall experience',
            'step': '0.5',
            'min': '0.5',
            'max': '5'
        }),
        label='Overall Rating'
    )
    review_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Write your review here'
        }),
        label='Review Text'
    )

class ServiceReviewForm(forms.Form):
    service_id = forms.IntegerField(widget=forms.HiddenInput())
    stars = forms.FloatField(
        min_value=0.5,
        max_value=5.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rate the service',
            'step': '0.5',
            'min': '0.5',
            'max': '5'
        }),
        label='Service Rating'
    )
    review_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Write your review here'
        }),
        label='Service Review Text'
    )