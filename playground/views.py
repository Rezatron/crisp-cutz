from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import BarberRegistrationForm, CustomerRegistrationForm, BarberLoginForm, CustomerLoginForm
from .models import Appointment, CustomUser, Barber, Customer
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.conf import settings
import requests

import sys

print(sys.path)

def home_page(request):
    return render(request, 'home.html')

def role_selection_view(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        if role == 'barber':
            return redirect('barber_register')
        elif role == 'customer':
            return redirect('customer_register')
    return render(request, 'home.html')

def barber_register(request):
    if request.method == 'POST':
        form = BarberRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            barber = form.save(commit=False)
            barber.latitude, barber.longitude = address_to_coordinates(barber.location)
            barber.save()
            # redirect to the login page:
            return HttpResponseRedirect('/barber/login/')
        else:
            # Print form errors
            print(form.errors)
    else:
        form = BarberRegistrationForm()

    return render(request, 'barber_registration.html', {'form': form})

def customer_register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.location = form.cleaned_data.get('location')
            customer.save()
            messages.success(request, 'Registration successful. You can now login.')
            return redirect('/customer/login')
    else:
        form = CustomerRegistrationForm()

    return render(request, 'registration/customer_registration.html', {'form': form})

def customer_login_view(request):
    if request.method == 'POST':
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password for customer')
    else:
        form = CustomerLoginForm()

    return render(request, 'registration/customer_login.html', {'form': form})

def barber_login_view(request):
    if request.method == 'POST':
        form = BarberLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('barber_dashboard')
            else:
                messages.error(request, 'Invalid username or password for barber')
    else:
        form = BarberLoginForm()

    return render(request, 'registration/barber_login.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('home')  # Changed 'home_page' to 'home'

@login_required
def dashboard(request):
    return render(request, 'customer_templates/customer_dashboard.html')


def address_to_coordinates(address):
    params = {
        'address': address,
        'key': settings.GOOGLE_MAPS_API_KEY
    }
    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json', params=params)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            lat = data['results'][0]['geometry']['location']['lat']
            lng = data['results'][0]['geometry']['location']['lng']
            return lat, lng
    return None, None





@login_required
def explore(request):
    customer = request.user.customer
    customer.latitude, customer.longitude = address_to_coordinates(customer.location)
    barbers = Barber.objects.all()  # Retrieve all Barber instances

    # Update the location data for each barber and create a list of barbers with their details
    barbers_details = []
    for barber in barbers:
        lat, lng = address_to_coordinates(barber.location)
        barber.latitude = lat
        barber.longitude = lng
        barber.save()

        barbers_details.append({
            'name': barber.first_name + ' ' + barber.last_name,  # replace with the correct attributes
            'location': barber.location,
            'latitude': barber.latitude,
            'longitude': barber.longitude,
            # Add any other details you want to display
        })

    context = {
        'customer': customer,
        'latitude': customer.latitude,
        'longitude': customer.longitude,
        'barbers_details': barbers_details,
    }
    return render(request, 'customer_templates/customer_explore.html', context)

@login_required
def appointments(request):
    return render(request, 'customer_templates/customer_appointments.html')

@login_required
def profile(request):
    return render(request, 'customer_templates/customer_profile.html')

@login_required
def barber_dashboard(request):
    barber = request.user.barber
    appointments = Appointment.objects.filter(barber=barber)
    return render(request, 'barber_templates/barber_dashboard.html', {'appointments': appointments})

@login_required
def barber_appointments(request):
    barber = request.user.barber
    appointments = Appointment.objects.filter(barber=barber)
    return render(request, 'barber_templates/barber_appointments.html', {'appointments': appointments})



@login_required
def barber_reports(request):
    # You would need to define what data you want to pass for reports
    return render(request, 'barber_templates/barber_reports.html')

@login_required
def barber_profile(request):
    barber = request.user.barber
    return render(request, 'barber_templates/barber_profile.html', {'barber': barber})

@login_required
def barber_settings(request):
    # You would need to define what data you want to pass for settings
    return render(request, 'barber_templates/barber_settings.html')



def list_customers(request):
    customers_with_usernames = Customer.objects.select_related('user')
    customer_usernames = [customer.user.username for customer in customers_with_usernames]
    return render(request, 'your_template.html', {'customer_usernames': customer_usernames})