# playground/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Appointment
from .tasks import schedule_review_creation

@receiver(post_save, sender=Appointment)
def create_review(sender, instance, created, **kwargs):
    if created:
        end_time = instance.end_time
        if end_time:
            # Schedule the review creation task to run at the appointment's end_time
            schedule_review_creation.apply_async((instance.id,), eta=end_time)
