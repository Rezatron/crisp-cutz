# utils.py
from .models import Appointment, Availability

def is_barber_available(barber, start_time, end_time):
    availabilities = Availability.objects.filter(barber=barber, is_available=True)
    for availability in availabilities:
        if availability.start_time <= start_time < availability.end_time and availability.start_time < end_time <= availability.end_time:
            return True
    return False
