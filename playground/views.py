from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import BarberRegistrationForm, CustomerRegistrationForm, BarberLoginForm, CustomerLoginForm
from .models import Appointment, CustomUser, Barber, Customer
from django.contrib.auth.decorators import login_required
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
        form = BarberRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. You can now login.')
            return redirect('login')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = BarberRegistrationForm()

    return render(request, 'registration/barber_registration.html', {'form': form})

def customer_register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. You can now login.')
            return redirect('login')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = CustomerRegistrationForm()

    return render(request, 'customer_registration.html', {'form': form})

def customer_login_view(request):
    error_message = None
    if request.method == 'POST':
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                error_message = 'Invalid username or password'
    else:
        form = CustomerLoginForm()
    return render(request, 'registration/customer_login.html', {'form': form, 'error_message': error_message})

def barber_login_view(request):
    error_message = None
    if request.method == 'POST':
        form = BarberLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None and hasattr(user, 'barber') and user.barber is not None:
                login(request, user)
                return redirect('barber_dashboard')
            else:
                error_message = 'Invalid username or password for barber'
    else:
        form = BarberLoginForm()
    return render(request, 'registration/barber_login.html', {'form': form, 'error_message': error_message})


def logout_customer(request):
    logout(request)
    return redirect('customer_login')

def dashboard(request):
    return render(request, 'dashboard.html')

def explore(request):
    return render(request, 'explore.html')

def appointments(request):
    return render(request, 'appointments.html')

def profile(request):
    return render(request, 'profile.html')


def barber_dashboard(request):
    barber = request.user.barber
    appointments = Appointment.objects.filter(barber=barber)
    return render(request, 'barber_dashboard.html', {'appointments': appointments})