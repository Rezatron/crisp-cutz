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

    if request.method == 'POST':
        form = AppointmentForm(request.POST, initial={'barber': barber_id})

        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.save()
            form.save_m2m()

            # Redirect to the confirmation page
            return redirect('appointment_confirmation', appointment_id=appointment.id)
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = AppointmentForm(initial={'barber': barber_id})
        available_services = barber.services.all() if barber else []
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

def appointment_confirmation(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'appointments/confirmation.html', {'appointment': appointment})