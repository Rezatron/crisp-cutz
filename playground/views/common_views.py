from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
import requests
import json
from django.utils import timezone
import datetime

from ..forms import BarberRegistrationForm, CustomerRegistrationForm, BarberLoginForm, CustomerLoginForm, BarberUpdateForm, CustomerUpdateForm, AvailabilityForm
from ..models import Appointment, Barber, Customer, Availability

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

def logout_user(request):
    logout(request)
    return redirect('home')

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

def list_customers(request):
    customers_with_usernames = Customer.objects.select_related('user')
    customer_usernames = [customer.user.username for customer in customers_with_usernames]
    return render(request, 'your_template.html', {'customer_usernames': customer_usernames})
