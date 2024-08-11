from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.urls import reverse
from django.forms import modelformset_factory
import datetime
import json

from ..forms import BarberRegistrationForm, BarberLoginForm, BarberUpdateForm, AvailabilityForm, BarberServiceForm, ServiceForm
from ..models import Appointment, Barber, Availability, Service, BarberService
from .common_views import address_to_coordinates
from django.contrib.auth.decorators import login_required

def barber_register(request):
    if request.method == 'POST':
        form = BarberRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            barber = form.save(commit=False)
            barber.latitude, barber.longitude = address_to_coordinates(barber.location)
            barber.save()
            return HttpResponseRedirect(reverse('barber_login'))
        else:
            print(form.errors)
    else:
        form = BarberRegistrationForm()
    return render(request, 'barber_registration.html', {'form': form})

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

@login_required
def barber_dashboard(request):
    barber = request.user.barber
    appointments = Appointment.objects.filter(barber=barber)
    return render(request, 'barber_templates/barber_dashboard.html', {'appointments': appointments})

@login_required
def barber_appointments(request):
    barber = request.user.barber
    appointments = Appointment.objects.filter(barber=barber).order_by('date_time')
    
    # Fetch availability data
    today = timezone.now().date()
    availability = Availability.objects.filter(barber=barber, start_time__date__gte=today).order_by('start_time')

    # Format availability data for day/week view
    availability_by_day = {}
    for avail in availability:
        day = avail.start_time.date()
        if day not in availability_by_day:
            availability_by_day[day] = []
        availability_by_day[day].append(avail)

    # Fetch and format availability data for the monthly view
    start_of_month = today.replace(day=1)
    end_of_month = (today.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
    monthly_availability = Availability.objects.filter(barber=barber, start_time__date__range=[start_of_month, end_of_month]).order_by('start_time')

    availability_by_day_monthly = {}
    for avail in monthly_availability:
        day = avail.start_time.date()
        if day not in availability_by_day_monthly:
            availability_by_day_monthly[day] = []
        availability_by_day_monthly[day].append(avail)

    return render(request, 'barber_templates/barber_appointments.html', {
        'appointments': appointments,
        'availability_by_day': availability_by_day,
        'availability_by_day_monthly': availability_by_day_monthly,
        'current_month': today.strftime('%B %Y'),
    })


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
    barber = request.user.barber
    if request.method == 'POST':
        form = BarberUpdateForm(request.POST, request.FILES, instance=barber)
        if form.is_valid():
            barber = form.save(commit=False)
            barber.location = form.cleaned_data.get('location')
            barber.latitude, barber.longitude = address_to_coordinates(barber.location)
            barber.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('barber_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
            print(form.errors)
    else:
        form = BarberUpdateForm(instance=barber)
    return render(request, 'barber_templates/barber_profile.html', {'form': form})

@login_required
def barber_settings(request):
    barber = request.user.barber
    if request.method == 'POST':
        form = BarberUpdateForm(request.POST, instance=barber)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('barber_settings')
    else:
        form = BarberUpdateForm(instance=barber)
    return render(request, 'barber_templates/barber_settings.html', {'form': form})

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
    availabilities = barber.availabilities.all()
    return render(request, 'barber_templates/manage_availability.html', {'availability_form': availability_form, 'availabilities': availabilities})

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

@login_required
def set_availability(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            start_time = data['start_time']
            end_time = data['end_time']
            barber = request.user.barber

            start_datetime = timezone.make_aware(datetime.datetime.fromisoformat(start_time))
            end_datetime = timezone.make_aware(datetime.datetime.fromisoformat(end_time))

            availability, created = Availability.objects.update_or_create(
                barber=barber,
                start_time__date=start_datetime.date(),
                defaults={
                    'start_time': start_datetime,
                    'end_time': end_datetime,
                    'is_available': True
                }
            )

            return JsonResponse({'status': 'success'})
        except KeyError as e:
            return JsonResponse({'status': 'error', 'message': f'Missing key: {e}'}, status=400)
        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': f'Invalid date format: {e}'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def delete_availability(request):
    if request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            start_time = data['start_time']
            barber = request.user.barber

            start_datetime = timezone.make_aware(datetime.datetime.fromisoformat(start_time))

            deleted_count, _ = Availability.objects.filter(
                barber=barber,
                start_time=start_datetime
            ).delete()

            if deleted_count > 0:
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'No availability found to delete'}, status=404)
        except KeyError as e:
            return JsonResponse({'status': 'error', 'message': f'Missing key: {e}'}, status=400)
        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': f'Invalid date format: {e}'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def get_availability_for_date(request):
    if request.method == 'GET':
        date_str = request.GET.get('date')
        if not date_str:
            return JsonResponse({'status': 'error', 'message': 'Date parameter is missing'}, status=400)
        try:
            start_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            start_date = timezone.make_aware(datetime.datetime.combine(start_date, datetime.datetime.min.time()))
            barber = request.user.barber
            availabilities = barber.availabilities.filter(start_time__date=start_date)
            availability_list = [{
                'start_time': availability.start_time.isoformat(),
                'end_time': availability.end_time.isoformat(),
            } for availability in availabilities]
            return JsonResponse({'status': 'success', 'data': availability_list})
        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': f'Invalid date format: {e}'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def barber_services(request, barber_id):
    barber = get_object_or_404(Barber, id=barber_id)
    services = barber.services.all()
    return render(request, 'barbers/services.html', {'barber': barber, 'services': services})

@login_required
def create_service(request):
    if request.method == 'POST':
        service_form = ServiceForm(request.POST)
        if service_form.is_valid():
            service = service_form.save()
            barber = request.user.barber
            if not BarberService.objects.filter(barber=barber, service=service).exists():
                BarberService.objects.create(
                    barber=barber,
                    service=service,
                    price=service.price,
                    duration=service.duration
                )
            messages.success(request, 'Service created successfully!')
            return redirect('manage_services')
    else:
        service_form = ServiceForm()
    return render(request, 'barber_templates/create_service.html', {'service_form': service_form})

@login_required
def manage_services(request):
    barber = request.user.barber
    services = barber.services.all()
    return render(request, 'barber_templates/manage_services.html', {'services': services})
