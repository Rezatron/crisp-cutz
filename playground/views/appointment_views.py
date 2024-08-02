from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.http import JsonResponse
from ..models import Barber, Service, Appointment, AppointmentService
from ..forms import AppointmentForm
import logging

logger = logging.getLogger(__name__)

def create_appointment(request, barber_id=None):
    barber = None
    if barber_id:
        barber = get_object_or_404(Barber, id=barber_id)

    if request.method == 'POST':
        print(f"POST data: {request.POST}")  # Debugging line
        form = AppointmentForm(request.POST)
        if form.is_valid():
            print("Form is valid.")  # Debugging line
            appointment = form.save(commit=False)
            appointment.user = request.user
            if barber:
                appointment.barber = barber
            appointment.save()
            form.save_m2m()
            print("Appointment saved successfully.")  # Debugging line
            return JsonResponse({'message': 'Appointment created successfully!', 'redirect_url': reverse('appointments_list')})
        else:
            errors = form.errors.as_json()
            print(f"Form errors: {errors}")  # Debugging line
            return JsonResponse({'errors': errors}, status=400)
    else:
        initial_data = {'barber': barber_id} if barber else {}
        print(f"Initial data for form: {initial_data}")  # Debugging line
        form = AppointmentForm(initial=initial_data)
    
    return render(request, 'appointments/create.html', {'form': form, 'barber': barber})





@login_required
def appointment_list(request):
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'appointments/list.html', {'appointments': appointments})

@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment_services = AppointmentService.objects.filter(appointment=appointment)
    return render(request, 'appointments/detail.html', {'appointment': appointment, 'appointment_services': appointment_services})
