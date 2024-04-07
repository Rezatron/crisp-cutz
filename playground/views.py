from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import BarberRegistrationForm, CustomerRegistrationForm
from django.contrib.auth import views as auth_views, authenticate, login, logout
from django.contrib import messages

def home_page(request):
    return render(request, 'home.html')

def role_selection_view(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        if role == 'barber':
            return redirect('barber_register')  # Redirect to barber registration page
        elif role == 'customer':
            return redirect('customer_register')  # Redirect to customer registration page
    return render(request, 'home.html')

def barber_register(request):
    if request.method == 'POST':
        form = BarberRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to the login page after successful registration
    else:
        form = BarberRegistrationForm()
    return render(request, 'registration/barber_registration.html', {'form': form})

def customer_register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after successful registration
    else:
        form = CustomerRegistrationForm()
    return render(request, 'customer_registration.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        # Hardcoded username and password for debugging purposes
        hardcoded_username = "test_user"
        hardcoded_password = "test_password"

        # Compare received username and password with hardcoded values
        if request.POST.get('username') == hardcoded_username and request.POST.get('password') == hardcoded_password:
            # Authentication successful, proceed with login
            return redirect('dashboard')
        else:
            # Authentication failed
            return render(request, 'login.html', {'error_message': 'Invalid username or password'})
    else:
        return render(request, 'login.html')


def dashboard(request):
       return render(request, 'dashboard.html')