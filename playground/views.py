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
            barber = form.save()  # Save the model immediately, no need for commit=False
            messages.success(request, 'Registration successful. You can now login.')
            return redirect('login')
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

@login_required
def explore(request):
    return render(request, 'customer_templates/customer_explore.html')

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
