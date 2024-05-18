from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Barber, Customer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, get_user_model

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

class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = Customer
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone_number', 'notification_preferences', 'address']



User = get_user_model()

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