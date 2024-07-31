from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from ..forms import CustomerRegistrationForm, CustomerLoginForm, CustomerUpdateForm
from ..models import Customer, Barber
from django.contrib.auth.decorators import login_required
from .common_views import address_to_coordinates
from django.urls import reverse


def customer_register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.location = form.cleaned_data.get('location')
            customer.save()
            messages.success(request, 'Registration successful. You can now login.')
            return redirect(reverse('customer_login'))
        else:
            # Print or log the form errors for debugging
            print(form.errors)
            messages.error(request, 'Please correct the errors below.')
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

@login_required
def dashboard(request):
    return render(request, 'customer_templates/customer_dashboard.html')

@login_required
def explore(request):
    customer = request.user.customer
    customer.latitude, customer.longitude = address_to_coordinates(customer.location)
    barbers = Barber.objects.all()

    barbers_details = []
    for barber in barbers:
        lat, lng = address_to_coordinates(barber.location)
        barber.latitude = lat
        barber.longitude = lng
        barber.save()

        barbers_details.append({
            'id': barber.id,
            'name': barber.first_name + ' ' + barber.last_name,
            'location': barber.location,
            'latitude': barber.latitude,
            'longitude': barber.longitude,
            'bio': str(barber.bio),
            'experience_years': str(barber.experience_years),
            'service_menu': str(barber.service_menu),
            'profile_picture_url': str(barber.profile_picture.url) if barber.profile_picture else None,
        })
    print(barbers_details)
    context = {
        'customer': customer,
        'latitude': customer.latitude,
        'longitude': customer.longitude,
        'barbers_details': barbers_details,
        'has_barbers': bool(barbers_details),  # Add this line
    }
    return render(request, 'customer_templates/customer_explore.html', context)


@login_required
def appointments(request):
    return render(request, 'customer_templates/customer_appointments.html')

@login_required
def profile(request):
    form = CustomerUpdateForm(instance=request.user.customer)
    return render(request, 'customer_templates/customer_profile.html', {'form': form})

@login_required
def update_customer(request):
    if request.method == 'POST':
        form = CustomerUpdateForm(request.POST, instance=request.user.customer)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.location = form.cleaned_data.get('location')
            customer.latitude, customer.longitude = address_to_coordinates(customer.location)
            customer.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('customer_profile')
        else:
            print(form.errors)
    else:
        form = CustomerUpdateForm(instance=request.user.customer)
    return render(request, 'customer_templates/customer_profile.html', {'form': form})
