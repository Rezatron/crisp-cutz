# tasks.py
from celery import shared_task
from .models import Appointment, Notification
import logging

logger = logging.getLogger('playground')

@shared_task
def schedule_review_creation(appointment_id):
    logger.debug(f"Task started for appointment ID: {appointment_id}")
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        logger.debug(f"Appointment found: {appointment}")

        barber_name = f"{appointment.barber.first_name} {appointment.barber.last_name}" if appointment.barber else "Unknown Barber"

        # Create Notification here
        Notification.objects.create(
            user=appointment.user,
            notification_type='review',
            message=f"Your appointment with {barber_name} has ended. Please leave a review.",
            appointment=appointment
        )
        logger.debug(f"Notification created for user: {appointment.user.id} for appointment ID: {appointment.id}")

    except Appointment.DoesNotExist:
        logger.error(f"Appointment ID {appointment_id} does not exist")
    except Exception as e:
        logger.error(f"Error creating notification for appointment ID {appointment_id}: {e}")
