from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import (BarberRegistrationForm, CustomerRegistrationForm,
                    BarberLoginForm, CustomerLoginForm, BarberUpdateForm,
                    CustomerUpdateForm, AvailabilityForm)
from .models import Appointment, Barber, Customer, Availability
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.conf import settings
import requests
from django.views.decorators.csrf import csrf_exempt
import json
import datetime  # Import datetime

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
            return HttpResponseRedirect('/barber/login/')
        else:
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
    return redirect('home')

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
    barbers = Barber.objects.all()

    barbers_details = []
    for barber in barbers:
        lat, lng = address_to_coordinates(barber.location)
        barber.latitude = lat
        barber.longitude = lng
        barber.save()

        barbers_details.append({
            'name': barber.first_name + ' ' + barber.last_name,
            'location': barber.location,
            'latitude': barber.latitude,
            'longitude': barber.longitude,
            'bio': str(barber.bio),
            'experience_years': str(barber.experience_years),
            'service_menu': str(barber.service_menu),
            'profile_picture_url': str(barber.profile_picture.url) if barber.profile_picture else None,
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
    return render(request, 'barber_templates/barber_reports.html')

@login_required
def barber_profile(request):
    if request.method == 'POST':
        form = BarberUpdateForm(request.POST, request.FILES, instance=request.user.barber)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('barber_profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = BarberUpdateForm(instance=request.user.barber)
    return render(request, 'barber_templates/barber_profile.html', {'form': form})

@login_required
def update_barber(request):
    if request.method == 'POST':
        form = BarberUpdateForm(request.POST, instance=request.user.barber)
        if form.is_valid():
            barber = form.save(commit=False)
            barber.location = form.cleaned_data.get('location')
            barber.latitude, barber.longitude = address_to_coordinates(barber.location)
            barber.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('barber_profile')
        else:
            print(form.errors)
    else:
        form = BarberUpdateForm(instance=request.user.barber)
    return render(request, 'barber_templates/barber_profile.html', {'form': form})

@login_required
def barber_settings(request):
    barber = request.user.barber

    if request.method == 'POST':
        # Handling the form submission for barber settings (if any)
        barber_update_form = BarberUpdateForm(request.POST, request.FILES, instance=barber)
        if barber_update_form.is_valid():
            barber_update_form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('barber_settings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Initialize form for GET requests
        barber_update_form = BarberUpdateForm(instance=barber)

    return render(request, 'barber_templates/barber_settings.html', {
        'barber_update_form': barber_update_form,
    })

@login_required
def manage_availability(request):
    barber = request.user.barber

    if request.method == 'POST':
        availability_form = AvailabilityForm(request.POST)
        if availability_form.is_valid():
            availability = availability_form.save(commit=False)
            availability.barber = barber
            availability.save()
            messages.success(request, 'Availability updated successfully!')
            return redirect('manage_availability')
        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        availability_form = AvailabilityForm()

    # Retrieve current availabilities
    availabilities = barber.availabilities.all()

    return render(request, 'barber_templates/manage_availability.html', {
        'availability_form': availability_form,
        'availabilities': availabilities,
    })

@login_required
def get_availability(request):
    barber = request.user.barber
    availabilities = barber.availabilities.all()
    availability_list = []

    for availability in availabilities:
        availability_list.append({
            'id': availability.id,
            'title': 'Available',
            'start': availability.start_time.isoformat(),
            'end': availability.end_time.isoformat(),
        })

    return JsonResponse(availability_list, safe=False)

@csrf_exempt
@login_required
def set_availability(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            start_time = data['start_time']
            end_time = data['end_time']
            barber = request.user.barber

            # Convert the date and time strings to datetime objects
            start_datetime = datetime.datetime.fromisoformat(start_time)
            end_datetime = datetime.datetime.fromisoformat(end_time)

            Availability.objects.create(
                barber=barber,
                start_time=start_datetime,
                end_time=end_datetime,
                is_available=True
            )
            return JsonResponse({'status': 'success'})
        except KeyError as e:
            return JsonResponse({'status': 'error', 'message': f'Missing key: {e}'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def list_customers(request):
    customers_with_usernames = Customer.objects.select_related('user')
    customer_usernames = [customer.user.username for customer in customers_with_usernames]
    return render(request, 'your_template.html', {'customer_usernames': customer_usernames})
