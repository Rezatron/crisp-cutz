from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.http import JsonResponse
from ..models import Barber, Service, Appointment, AppointmentService, BarberService, Availability
from ..forms import AppointmentForm
import logging
from datetime import timedelta 
from django.http import HttpResponse


logger = logging.getLogger('playground')
@login_required
def create_appointment(request, barber_id=None):
    barber = get_object_or_404(Barber, id=barber_id) if barber_id else None

    if request.method == 'POST':
        form = AppointmentForm(request.POST, initial={'barber': barber_id})

        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user

            # Get the selected service IDs from the form
            selected_service_ids = form.cleaned_data['services']
            barber_services = BarberService.objects.filter(barber=appointment.barber, service__in=selected_service_ids)

            logger.debug(f"Creating appointment with barber ID: {appointment.barber.id}")
            logger.debug(f"Selected Service IDs: {selected_service_ids}")

            # Calculate total duration and price from BarberService
            total_duration = timedelta()
            total_price = 0
            for service in barber_services:
                duration = service.duration
                price = service.price
                logger.debug(f"BarberService ID: {service.id}, Duration: {duration} (Type: {type(duration)}), Price: {price}")
                total_duration += duration
                total_price += price

            logger.debug(f"Total Duration from BarberService: {total_duration}")
            logger.debug(f"Total Price from BarberService: {total_price}")

            # Set end_time based on total_duration
            if total_duration:
                appointment.end_time = appointment.date_time + total_duration
                logger.debug(f"Calculated End Time: {appointment.end_time}")

            # Check barber availability
            if not is_barber_available(appointment.barber, appointment.date_time, appointment.end_time):
                return JsonResponse({'errors': 'The barber is not available at the selected time.'}, status=400)

            # Save the appointment with calculated end_time
            appointment.save()
            form.save_m2m()  # Save the many-to-many relationships

            # Block out the availability
            block_barber_availability(appointment.barber, appointment.date_time, appointment.end_time)

            return JsonResponse({
                'success': True,
                'appointment': {
                    'barber': {
                        'first_name': appointment.barber.first_name,
                        'last_name': appointment.barber.last_name,
                    },
                    'date_time': appointment.date_time.strftime("%B %d, %Y %I:%M %p"),
                    'end_time': appointment.end_time.strftime("%I:%M %p"),
                    'location': appointment.barber.location,
                    'services': [service.name for service in appointment.services.all()],
                    'total_price': total_price
                }
            })
        else:
            logger.debug(f"Form errors: {form.errors}")
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


def is_barber_available(barber, start_time, end_time):
    """Check if the barber is available for the requested time slot."""
    availabilities = Availability.objects.filter(
        barber=barber,
        is_available=True,
        start_time__lt=end_time,
        end_time__gt=start_time
    )

    for availability in availabilities:
        if availability.is_available_for_appointment(start_time, end_time):
            return True
    return False




def block_barber_availability(barber, start_time, end_time):
    """Block out the barber's availability for the given time slot."""
    overlapping_availabilities = Availability.objects.filter(
        barber=barber,
        is_available=True,
        start_time__lt=end_time,
        end_time__gt=start_time
    )

    for availability in overlapping_availabilities:
        if availability.start_time < start_time and availability.end_time > end_time:
            # Split the availability into two slots
            Availability.objects.create(
                barber=barber,
                start_time=availability.start_time,
                end_time=start_time,
                is_available=True
            )
            Availability.objects.create(
                barber=barber,
                start_time=end_time,
                end_time=availability.end_time,
                is_available=True
            )
            availability.delete()
        elif availability.start_time < start_time:
            availability.end_time = start_time
            availability.save()
        elif availability.end_time > end_time:
            availability.start_time = end_time
            availability.save()
        else:
            availability.delete()



