from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from ..models import Appointment, Notification

@login_required
def check_notifications(request):
    now = timezone.now()
    ended_appointments = Appointment.objects.filter(end_time__lte=now, user=request.user, notified=False)
    notifications = []

    for appointment in ended_appointments:
        notifications.append({
            'id': appointment.id,
            'message': f'Your appointment with {appointment.barber.first_name} {appointment.barber.last_name} has ended. Please leave a review.'
        })
        appointment.notified = True
        appointment.save()

    # Clear notifications for deleted appointments
    Notification.objects.filter(user=request.user, appointment__isnull=True).delete()

    return JsonResponse({'notifications': notifications})