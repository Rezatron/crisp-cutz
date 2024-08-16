# playground/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Appointment
from .tasks import schedule_review_creation
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Appointment)
def create_review(sender, instance, created, **kwargs):
    if created:
        end_time = instance.end_time
        if end_time and end_time > timezone.now():
            logger.debug(f"Scheduling review creation for appointment ID {instance.id} at {end_time}")
            schedule_review_creation.apply_async((instance.id,), eta=end_time)
        else:
            logger.debug(f"Scheduling immediate review creation for appointment ID {instance.id}")
            schedule_review_creation.apply_async((instance.id,))