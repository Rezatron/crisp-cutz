# appointment_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from ..models import Barber, Service, Appointment, AppointmentService
from ..forms import AppointmentForm
from ..utils import is_barber_available  # Import from utils.py

import logging

logger = logging.getLogger(__name__)

@login_required
def create_appointment(request, barber_id=None):
    barber = None
    if barber_id:
        barber = get_object_or_404(Barber, id=barber_id)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            if barber:
                appointment.barber = barber
            appointment.save()
            
            for service in form.cleaned_data['services']:
                AppointmentService.objects.create(appointment=appointment, service=service)
            
            return redirect('appointment_detail', appointment.id)
    else:
        form = AppointmentForm()
    
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
