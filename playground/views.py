from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import BarberRegistrationForm, CustomerRegistrationForm, BarberLoginForm
from django.contrib import messages

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
            return redirect('login')
    else:
        form = BarberRegistrationForm()
    
    return render(request, 'registration/barber_registration.html', {'form': form})

def customer_register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'customer_registration.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error_message': 'Invalid username or password'})
    else:
        return render(request, 'login.html')

def barber_login_view(request):
    if request.method == 'POST':
        form = BarberLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('barber_dashboard')
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = BarberLoginForm()
    return render(request, 'barber_login.html', {'form': form})

def address_selection_view(request):
    return render(request, 'address_selection.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def explore(request):
    return render(request, 'explore.html')

def appointments(request):
    return render(request, 'appointments.html')

def profile(request):
    return render(request, 'profile.html')