from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import random
import string



class CustomUser(AbstractUser):
    # Existing code

    def save(self, *args, **kwargs):
        if not self.pk and not self.password:
            self.set_password(''.join(random.choices(string.ascii_letters + string.digits, k=12)))  # Generate a random password
        super().save(*args, **kwargs)

    class Meta:
        abstract = True  # Make sure this model is not created in the database

class Customer(CustomUser):
    # Fields specific to customers
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    notification_preferences = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    # Add related_name for groups
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        related_name='customer_groups',
        related_query_name='customer',
    )

    # Add related_name for user_permissions
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        related_name='customer_user_permissions',
        related_query_name='customer',
    )

    def __str__(self):
        return self.username

class Barber(CustomUser):
    # Fields specific to barbers
    name = models.CharField(max_length=150)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='barber_profiles/', blank=True, null=True)
    experience_years = models.PositiveIntegerField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    service_menu = models.TextField(blank=True, null=True)
    booking_preferences = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, default='Default Location')  # Location field with default value
    specialization = models.CharField(max_length=100, default='General')  # Specialization field with default value

    # Add related_name for groups
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='barber_groups',
        related_query_name='barber',
    )

    # Add related_name for user_permissions
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='barber_user_permissions',
        related_query_name='barber',
    )

    def __str__(self):
        return self.username



class Haircut(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField()
    # Add more fields as needed

class Appointment(models.Model):
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE)
    haircut = models.ForeignKey(Haircut, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    date_time = models.DateTimeField()

    def __str__(self):
        return f"Appointment for {self.haircut} with {self.barber} on {self.date_time}"

class Review(models.Model):
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    stars = models.IntegerField()
    haircut_type = models.CharField(max_length=100)
    review_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Review for {self.barber} by {self.user}"
