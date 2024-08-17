from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password
import random
import string
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta, time
from django.contrib.auth.models import User

import logging

# Configure logging (for quick debugging purposes)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('playground')
logger = logging.getLogger('playground')
logger.setLevel(logging.DEBUG) 



class CustomUser(AbstractUser):
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and not self.password:
            self.password = make_password(''.join(random.choices(string.ascii_letters + string.digits, k=12)))  # Generate a random password
        super().save(*args, **kwargs)

class Customer(CustomUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    notification_preferences = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    customer_groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_name="customer_groups",
        related_query_name="customer",
    )

    def __str__(self):
        return self.username

class Barber(CustomUser):
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='barber_profiles/', blank=True, null=True)
    experience_years = models.PositiveIntegerField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    service_menu = models.TextField(blank=True, null=True)
    booking_preferences = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    specialization = models.CharField(max_length=100, default='General')
    services = models.ManyToManyField('Service', related_name='barbers')

    class Meta:
        ordering = ['id', 'username', 'email', 'first_name', 'last_name', 'bio', 'experience_years', 'is_available', 'service_menu', 'booking_preferences', 'location', 'specialization',]
        permissions = [
            ("view_appointment", "Can view appointments"),
            ("delete_appointment", "Can delete appointments"),
        ]

    def __str__(self):
        return self.username

class Availability(models.Model):
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='availabilities')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.barber.username} - {self.start_time} to {self.end_time}"

    def is_current(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time and self.is_available

    def is_available_for_appointment(self, start_time, end_time):
        """Check if the availability covers the requested appointment time."""
        return self.start_time <= start_time and self.end_time >= end_time and self.is_available

class Service(models.Model):
    name = models.CharField(max_length=100)
    duration = models.DurationField()  # Duration of the service
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name



class BarberService(models.Model):
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField()

    class Meta:
        unique_together = ('barber', 'service')

    def __str__(self):
        return f"{self.barber.username} - {self.service.name}"
    


class Appointment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_appointments')
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='barber_appointments')
    services = models.ManyToManyField(Service, through='AppointmentService')
    date_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Appointment with {self.barber} on {self.date_time}"

    def save(self, *args, **kwargs):
        if self.pk is None and not self.end_time:  # Only calculate end_time if this is a new instance
            super().save(*args, **kwargs)  # Save the instance to get an ID

            # Calculate total duration of all services
            total_duration = timedelta()
            barber_services = BarberService.objects.filter(barber=self.barber, service__in=self.services.all())

            logger.debug(f"Calculating total duration for appointment ID: {self.id}")
            logger.debug(f"Barber Services: {list(barber_services)}")

            for service in barber_services:
                duration = service.duration
                logger.debug(f"BarberService ID: {service.id}, Duration: {duration} (Type: {type(duration)})")
                total_duration += duration

            logger.debug(f"Total Duration from BarberService: {total_duration}")

            if total_duration:
                self.end_time = self.date_time + total_duration
                logger.debug(f"Calculated End Time: {self.end_time}")
                super().save(*args, **kwargs)  # Save again to update end_time
        else:
            super().save(*args, **kwargs)




class AppointmentService(models.Model):
    appointment = models.ForeignKey('Appointment', on_delete=models.CASCADE)
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.appointment} - {self.service.name}"





class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_reviews')
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='barber_reviews')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='appointment_reviews', null=True, blank=True)
    overall_experience = models.FloatField()  # Removed default value
    review_text = models.TextField(blank=True, null=True)  # Optional review text
    created_at = models.DateTimeField(default=timezone.now)  # Default value

    def __str__(self):
        return f"Review for {self.barber} by {self.user} for appointment {self.appointment}"


class ServiceReview(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='service_reviews')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_reviews')
    stars = models.FloatField()  # Removed default value
    review_text = models.TextField(blank=True, null=True)  # Optional review text for the service

    def __str__(self):
        return f"Review for {self.service} in review ID: {self.review.id}"


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('review', 'Review'),
        ('offer', 'Offer'),
        ('system', 'System'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)  # Add this line

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"
