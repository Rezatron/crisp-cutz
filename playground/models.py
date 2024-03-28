#models.py real-file
from django.db import models

class Barber(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='barber_profiles/', blank=True, null=True)
    experience_years = models.PositiveIntegerField(blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

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
