from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.http import JsonResponse
from ..models import Barber, Service, Appointment, AppointmentService
from ..forms import AppointmentForm
import logging

logger = logging.getLogger(__name__)


@login_required
def create_appointment(request, barber_id=None):
    barber = get_object_or_404(Barber, id=barber_id) if barber_id else None
    print(f"Found Barber with ID: {barber_id}")
    print("Request Method:", request.method)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, initial={'barber': barber_id})
        print("Request Data:", request.POST)
        print("Form valid:", form.is_valid())
        print("Form errors:", form.errors)
        
        if form.is_valid():
            appointment = form.save(commit=False)  # Create the appointment instance
            appointment.user = request.user  # Set the user here
            appointment.save()  # Save the instance first to get an ID
            form.save_m2m()     # Save many-to-many relationships
            return JsonResponse({'message': 'Appointment created successfully.'}, status=201)
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = AppointmentForm(initial={'barber': barber_id})
        available_services = barber.services.all() if barber else []
        print("Available Barbers in form:", Barber.objects.all())
        print(f"Available Services for Barber {barber_id}:", available_services)

        return render(request, 'appointments/create.html', {
            'form': form,
            'barber': barber,
            'available_services': available_services,
        })





@login_required
def appointment_list(request):
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'appointments/list.html', {'appointments': appointments})

@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment_services = AppointmentService.objects.filter(appointment=appointment)
    return render(request, 'appointments/detail.html', {'appointment': appointment, 'appointment_services': appointment_services})
