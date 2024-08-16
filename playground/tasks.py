# playground/tasks.py
from celery import shared_task
from .models import Appointment, Review, ServiceReview
import logging

logger = logging.getLogger('playground')

@shared_task
def schedule_review_creation(appointment_id):
    logger.debug(f"Task started for appointment ID: {appointment_id}")
    try:
        # Attempt to retrieve the appointment
        appointment = Appointment.objects.get(id=appointment_id)
        logger.debug(f"Appointment found: {appointment}")

        # Create the overall review
        review = Review.objects.create(
            appointment=appointment,
            barber=appointment.barber,
            user=appointment.user,
            overall_experience=2.5,  # Default value for demonstration
            review_text="",
        )
        logger.debug(f"Review created: {review}")

        # Create service-specific reviews
        for service in appointment.services.all():
            service_review = ServiceReview.objects.create(
                review=review,
                service=service,
                stars=2.5,  # Default value for demonstration
            )
            logger.debug(f"ServiceReview created: {service_review}")

        logger.debug(f"Review and ServiceReviews created for appointment ID: {appointment_id}")

    except Appointment.DoesNotExist:
        logger.error(f"Appointment ID {appointment_id} does not exist")
    except Exception as e:
        logger.error(f"Error creating review for appointment ID {appointment_id}: {e}")
