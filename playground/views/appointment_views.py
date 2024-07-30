# appointment_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from ..models import Barber, Service, Appointment, AppointmentService
from ..forms import AppointmentForm
from ..utils import is_barber_available  # Import from utils.py

@login_required
def create_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            barber = form.cleaned_data['barber']
            services = form.cleaned_data['services']
            start_time = form.cleaned_data['date_time']
            # Calculate end_time based on the total duration of selected services
            total_duration = sum(service.duration.total_seconds() for service in services)
            end_time = start_time + timezone.timedelta(seconds=total_duration)

            # Check barber availability
            if not is_barber_available(barber, start_time, end_time):
                form.add_error(None, 'The barber is not available at this time.')
            else:
                appointment = form.save(commit=False)
                appointment.user = request.user
                appointment.end_time = end_time
                appointment.save()
                
                for service in services:
                    AppointmentService.objects.create(appointment=appointment, service=service)
                
                return redirect('appointment_detail', appointment.id)
    else:
        form = AppointmentForm()
    return render(request, 'appointments/create.html', {'form': form})

@login_required
def appointment_list(request):
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'appointments/list.html', {'appointments': appointments})

@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment_services = AppointmentService.objects.filter(appointment=appointment)
    return render(request, 'appointments/detail.html', {'appointment': appointment, 'appointment_services': appointment_services})
