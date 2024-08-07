from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from ..forms import CustomerRegistrationForm, CustomerLoginForm, CustomerUpdateForm
from ..models import Customer, Barber, Appointment
from django.contrib.auth.decorators import login_required
from .common_views import address_to_coordinates
from django.urls import reverse

def customer_register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            Customer.objects.create(user=user, location=form.cleaned_data.get('location'))
            messages.success(request, 'Registration successful. You can now login.')
            return redirect(reverse('customer_login'))
        else:
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
        'has_barbers': bool(barbers_details),
    }
    return render(request, 'customer_templates/customer_explore.html', context)

@login_required
def customer_appointments(request):
    user = request.user
    try:
        customer = user.customer
        appointments = Appointment.objects.filter(user=customer)

        # Debugging: Print user and appointments count
        print(f"User: {user.username}")
        print(f"Number of appointments found: {appointments.count()}")
        for appointment in appointments:
            print(f"Appointment ID: {appointment.id}, Date and Time: {appointment.date_time}, User: {appointment.user.username}")

        return render(request, 'customer_templates/customer_appointments.html', {
            'appointments': appointments
        })
    except Customer.DoesNotExist:
        messages.error(request, "No customer profile found. Please complete your profile first.")
        return redirect('profile')

@login_required
def profile(request):
    try:
        customer = request.user.customer
        form = CustomerUpdateForm(instance=customer)
    except Customer.DoesNotExist:
        customer = Customer(user=request.user)
        form = CustomerUpdateForm(instance=customer)

    if request.method == 'POST':
        form = CustomerUpdateForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')

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
