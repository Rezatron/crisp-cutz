from django.contrib import admin
from .models import Barber, Customer, BarberService, Service


class BarberServiceInline(admin.TabularInline):
    model = BarberService
    extra = 1  # Number of extra forms

class ServiceAdmin(admin.ModelAdmin):
    inlines = [BarberServiceInline]




admin.site.register(Barber)
admin.site.register(Customer)
admin.site.register(BarberService)
admin.site.register(Service)