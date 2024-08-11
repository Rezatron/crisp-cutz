from django.contrib import admin
from .models import Barber, Customer, BarberService, Service, Appointment, AppointmentService, Availability

class BarberServiceInline(admin.TabularInline):
    model = BarberService
    extra = 1  # Number of extra forms

class AppointmentServiceInline(admin.TabularInline):
    model = AppointmentService
    extra = 1  # Number of extra forms

class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 1  # Number of extra forms

class ServiceAdmin(admin.ModelAdmin):
    inlines = [BarberServiceInline]

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'barber', 'date_time', 'end_time')
    inlines = [AppointmentServiceInline]

class BarberAdmin(admin.ModelAdmin):
    inlines = [AvailabilityInline]  # Add the Availability inline here

admin.site.register(Barber, BarberAdmin)
admin.site.register(Customer)
admin.site.register(BarberService)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(AppointmentService)
admin.site.register(Availability)
