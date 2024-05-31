from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password
import random
import string

from django.contrib.auth.models import User
from django.conf import settings
from django.db import models



class CustomUser(AbstractUser):
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and not self.password:
            self.password = make_password(''.join(random.choices(string.ascii_letters + string.digits, k=12)))  # Generate a random password
        super().save(*args, **kwargs)

class Customer(CustomUser):
    # Fields specific to customers

    phone_number = models.CharField(max_length=20, blank=True, null=True)
    notification_preferences = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    # Override the groups field
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
    
    specialization = models.CharField(max_length=100, default='General')  # Specialization field with default value

    class Meta:
        ordering = ['id', 'username', 'email', 'first_name', 'last_name', 'bio', 'experience_years', 'is_available', 'service_menu', 'booking_preferences', 'location', 'specialization',]
        permissions = [
            # existing permissions here
            ("view_appointment", "Can view appointments"),
            ("delete_appointment", "Can delete appointments"),
        ]

    def __str__(self):
        return self.username

class Haircut(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField()
    # Add more fields as needed

class Appointment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_appointments')
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='barber_appointments')
    haircut = models.ForeignKey(Haircut, on_delete=models.CASCADE)
    date_time = models.DateTimeField()

    def __str__(self):
        return f"Appointment for {self.haircut} with {self.barber} on {self.date_time}"

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_reviews')
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='barber_reviews')
    stars = models.IntegerField()
    haircut_type = models.CharField(max_length=100)
    review_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Review for {self.barber} by {self.user}"