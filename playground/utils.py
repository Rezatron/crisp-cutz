# utils.py
from .models import Appointment

def is_barber_available(barber, start_time, end_time):
    availabilities = barber.availabilities.filter(
        start_time__lte=start_time, end_time__gte=end_time, is_available=True
    )
    overlapping_appointments = Appointment.objects.filter(
        barber=barber, date_time__lt=end_time, end_time__gt=start_time
    )
    return availabilities.exists() and not overlapping_appointments.exists()
