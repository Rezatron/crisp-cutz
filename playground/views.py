from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import BarberRegistrationForm, CustomerRegistrationForm


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
            return redirect('login')  # Redirect to login page after successful registration
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