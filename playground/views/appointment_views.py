from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from ..models import Barber, Haircut, Appointment, Availability
from ..forms import AppointmentForm

@login_required
def create_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            barber = form.cleaned_data['barber']
            haircut = form.cleaned_data['haircut']
            start_time = form.cleaned_data['date_time']
            end_time = start_time + haircut.duration

            # Check barber availability
            if not is_barber_available(barber, start_time, end_time):
                form.add_error(None, 'The barber is not available at this time.')
            else:
                appointment = form.save(commit=False)
                appointment.user = request.user
                appointment.end_time = end_time  # Add end_time to the appointment
                appointment.save()
                return redirect('appointment_detail', appointment.id)
    else:
        form = AppointmentForm()
    return render(request, 'appointments/create.html', {'form': form})

def is_barber_available(barber, start_time, end_time):
    availabilities = barber.availabilities.filter(
        start_time__lte=start_time, end_time__gte=end_time, is_available=True)
    overlapping_appointments = Appointment.objects.filter(
        barber=barber, date_time__lt=end_time, end_time__gt=start_time)
    return availabilities.exists() and not overlapping_appointments.exists()

@login_required
def appointment_list(request):
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'appointments/list.html', {'appointments': appointments})

@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'appointments/detail.html', {'appointment': appointment})
