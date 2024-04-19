from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_protect
from .forms import BarberRegistrationForm, CustomerRegistrationForm, BarberLoginForm
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
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Login the user
            login(request, user)
            return redirect('dashboard')
        else:
            # Authentication failed
            return render(request, 'login.html', {'error_message': 'Invalid username or password'})
    else:
        return render(request, 'login.html')



def barber_login_view(request):
    print("Accessing barber_login_view")
    if request.method == 'POST':
        form = BarberLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('barber_dashboard')  # Redirect to barber dashboard
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = BarberLoginForm()
    
    return render(request, 'barber_login.html', {'form': form})


def dashboard(request):
    return render(request, 'dashboard.html')


def explore(request):
    return render(request, 'explore.html')


def appointments(request):
    return render(request, 'appointments.html')


def profile(request):
    return render(request, 'profile.html')
