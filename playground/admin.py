from django.contrib import admin
from .models import (
    Barber, Customer, BarberService, Service, Appointment, AppointmentService, 
    Availability, Review, ServiceReview, Notification
)

# Inlines
class BarberServiceInline(admin.TabularInline):
    model = BarberService
    extra = 1

class AppointmentServiceInline(admin.TabularInline):
    model = AppointmentService
    extra = 1

class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 1

# Admin Models
class ServiceAdmin(admin.ModelAdmin):
    inlines = [BarberServiceInline]

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'barber', 'date_time', 'end_time')
    inlines = [AppointmentServiceInline]

class BarberAdmin(admin.ModelAdmin):
    inlines = [AvailabilityInline]

# Registering models in the admin site
admin.site.register(Barber, BarberAdmin)
admin.site.register(Customer)
admin.site.register(BarberService)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(AppointmentService)
admin.site.register(Availability)

# Reviews Admin
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'barber', 'appointment', 'overall_experience', 'created_at')
    search_fields = ('user__username', 'barber__name', 'appointment__id')
    list_filter = ('barber', 'created_at')

class ServiceReviewAdmin(admin.ModelAdmin):
    list_display = ('review', 'service', 'stars')
    search_fields = ('review__user__username', 'service__name')
    list_filter = ('stars',)

admin.site.register(Review, ReviewAdmin)
admin.site.register(ServiceReview, ServiceReviewAdmin)

# Notifications Admin
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'message', 'read', 'created_at', 'appointment')
    search_fields = ('user__username', 'message')
    list_filter = ('notification_type', 'read', 'created_at')
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(read=True)
        self.message_user(request, "Selected notifications marked as read.")

    def mark_as_unread(self, request, queryset):
        queryset.update(read=False)
        self.message_user(request, "Selected notifications marked as unread.")

    mark_as_read.short_description = "Mark selected notifications as read"
    mark_as_unread.short_description = "Mark selected notifications as unread"

admin.site.register(Notification, NotificationAdmin)
