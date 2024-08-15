from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.urls import reverse
from django.forms import modelformset_factory
import json
from django.utils import timezone
from collections import OrderedDict
from datetime import datetime, timedelta, time
from ..forms import BarberRegistrationForm, BarberLoginForm, BarberUpdateForm, AvailabilityForm, BarberServiceForm, ServiceForm
from ..models import Appointment, Barber, Availability, Service, BarberService
from .common_views import address_to_coordinates
from django.contrib.auth.decorators import login_required
import logging
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger(__name__)


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
    today = timezone.now().date()
    date = request.GET.get('date')
    
    if date:
        try:
            selected_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today

    # Fetch appointments and availability for the selected date
    appointments = Appointment.objects.filter(
        barber=barber, date_time__date=selected_date
    ).order_by('date_time')

    availability = Availability.objects.filter(
        barber=barber, start_time__date=selected_date
    ).order_by('start_time')

    # Determine the earliest start and latest end times
    if appointments.exists() or availability.exists():
        earliest_start = min(
            [a.date_time for a in appointments] + [a.start_time for a in availability]
        )
        latest_end = max(
            [a.end_time for a in appointments] + [a.end_time for a in availability]
        )
    else:
        earliest_start = datetime.combine(selected_date, time(8, 0))  # Default to 08:00
        latest_end = datetime.combine(selected_date, time(16, 0))  # Default to 16:00

    # Create a combined list of events, both appointments and availability
    events = []

    # Helper function to convert time to pixel position
    def time_to_position(time, start_time):
        hour_diff = (time - start_time).total_seconds() // 3600
        minute_diff = ((time - start_time).total_seconds() % 3600) / 60
        return hour_diff * 60 + minute_diff  # 1 hour = 60px
    
    start_of_day = earliest_start.replace(minute=0, second=0, microsecond=0)
    end_of_day = latest_end.replace(minute=0, second=0, microsecond=0)

    for appointment in appointments:
        start_position = time_to_position(appointment.date_time, start_of_day)
        end_position = time_to_position(appointment.end_time, start_of_day)
        events.append({
            'type': 'appointment',
            'start_time': appointment.date_time,
            'end_time': appointment.end_time,
            'customer': appointment.user.username,
            'services': appointment.services.all(),
            'top_position': start_position,
            'height': end_position - start_position
        })
    
    for avail in availability:
        start_position = time_to_position(avail.start_time, start_of_day)
        end_position = time_to_position(avail.end_time, start_of_day)
        events.append({
            'type': 'availability',
            'start_time': avail.start_time,
            'end_time': avail.end_time,
            'top_position': start_position,
            'height': end_position - start_position
        })

    events.sort(key=lambda x: x['start_time'])

    # Generate time slots for the timeline based on the dynamic range
    total_hours = int((end_of_day - start_of_day).total_seconds() // 3600) + 1
    hours_list = [(start_of_day + timedelta(hours=i)).strftime('%H:%M') for i in range(total_hours)]

    # Calculate previous and next days
    prev_day = selected_date - timedelta(days=1)
    next_day = selected_date + timedelta(days=1)

    return render(request, 'barber_templates/barber_appointments.html', {
        'view_type': 'daily',
        'events': events,
        'selected_date': selected_date,
        'prev_day': prev_day,
        'next_day': next_day,
        'hours_list': hours_list
    })

@login_required
def monthly_appointments(request):
    barber = request.user.barber
    today = timezone.now().date()
    date = request.GET.get('date', today.strftime('%Y-%m-%d'))
    
    try:
        selected_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        selected_date = today

    first_day_of_month = selected_date.replace(day=1)
    last_day_of_month = (first_day_of_month + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    
    appointments = Appointment.objects.filter(
        barber=barber, date_time__date__range=[first_day_of_month, last_day_of_month]
    ).order_by('date_time')

    availability = Availability.objects.filter(
        barber=barber, start_time__date__range=[first_day_of_month, last_day_of_month]
    ).order_by('start_time')

    events = []

    for appointment in appointments:
        services = ', '.join([service.name for service in appointment.services.all()])
        events.append({
            'title': f"Appointment with {appointment.user.username}",
            'start': appointment.date_time.isoformat(),
            'end': appointment.end_time.isoformat(),
            'color': '#f8d7da',  # Light red background
            'textColor': '#dc3545',  # Red text for appointments
            'serviceName': services,
        })
    
    for avail in availability:
        events.append({
            'title': 'Available',
            'start': avail.start_time.isoformat(),
            'end': avail.end_time.isoformat(),
            'color': '#d4edda',  # Light green background
            'textColor': '#28a745',  # Green text for availability
        })

    return render(request, 'barber_templates/barber_monthly_appointments.html', {
        'view_type': 'monthly',
        'events': json.dumps(events),  # Ensure events are passed as JSON
        'selected_date': selected_date,
        'today': today
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

            # Ensure timezone-awareness before saving
            availability.start_time = timezone.make_aware(availability.start_time)
            availability.end_time = timezone.make_aware(availability.end_time)

            availability.save()
            messages.success(request, 'Availability updated successfully!')
            return redirect('manage_availability')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        availability_form = AvailabilityForm()
    
    availabilities = barber.availabilities.all()
    return render(request, 'barber_templates/manage_availability.html', {
        'availability_form': availability_form, 
        'availabilities': availabilities
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

@login_required
def set_availability(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.debug(f"Received data: {data}")
            start_time_str = data.get('start_time')
            end_time_str = data.get('end_time')
            barber = request.user.barber

            # Parse the start and end time using correct format
            start_datetime = datetime.fromisoformat(start_time_str)
            end_datetime = datetime.fromisoformat(end_time_str)

            # Convert to timezone-aware datetime objects
            start_datetime = timezone.make_aware(start_datetime)
            end_datetime = timezone.make_aware(end_datetime)

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
    return render(request, 'barber_templates/manage_service.html', {'service_form': service_form})

@login_required
def manage_services(request):
    barber = request.user.barber

    selected_service_id = request.GET.get('service_id')

    if request.method == 'POST':
        if 'create_service' in request.POST:
            # Handle the creation of a new service
            service_form = ServiceForm(request.POST)
            if service_form.is_valid():
                service = service_form.save()
                BarberService.objects.create(
                    barber=barber,
                    service=service,
                    price=service.price,
                    duration=service.duration
                )
                messages.success(request, 'Service created successfully!')
                return redirect('manage_services')

        elif 'edit_service' in request.POST:
            # Handle editing of an existing service
            barber_service = get_object_or_404(BarberService, pk=request.POST['edit_service_id'], barber=barber)
            service_form = ServiceForm(request.POST, instance=barber_service.service)
            
            if service_form.is_valid():
                # Save changes to the Service model
                updated_service = service_form.save()
                
                # Update the BarberService model if needed (usually not required if prices/durations are updated in Service model)
                barber_service.price = updated_service.price
                barber_service.duration = updated_service.duration
                barber_service.save()
                
                messages.success(request, 'Service updated successfully!')
                return redirect('manage_services')

    # If GET request, prefill the form if a service ID is provided
    if selected_service_id:
        barber_service = get_object_or_404(BarberService, pk=selected_service_id, barber=barber)
        form = ServiceForm(instance=barber_service.service)
    else:
        form = ServiceForm()

    # Render the template with the forms
    return render(request, 'barber_templates/manage_services.html', {
        'form': form,
        'service_form': ServiceForm(),
        'services': BarberService.objects.filter(barber=barber)
    })
