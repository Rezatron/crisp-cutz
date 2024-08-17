from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from ..models import Appointment, Review, ServiceReview, Service, Notification
from ..forms import ReviewForm, ServiceReviewForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_POST


import logging

logger = logging.getLogger(__name__)

@login_required
def fetch_appointment_details(request, appointment_id):
    logger.info(f"Fetching details for appointment ID: {appointment_id}")
    if request.method == 'GET':
        appointment = get_object_or_404(Appointment, id=appointment_id)
        services = Service.objects.filter(appointment=appointment)
        service_data = [{'id': service.id, 'name': service.name} for service in services]

        data = {
            'success': True,
            'appointment_id': appointment.id,
            'barber': f"{appointment.barber.first_name} {appointment.barber.last_name}",
            'services': service_data,
        }
        return JsonResponse(data)
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
@require_POST
def submit_review(request):
    appointment_id = request.POST.get('appointment_id')
    overall_experience = request.POST.get('overall_experience')
    review_text = request.POST.get('review_text')
    service_count = int(request.POST.get('service_count'))

    try:
        appointment = Appointment.objects.get(id=appointment_id, user=request.user)
        review = Review.objects.create(
            user=request.user,
            barber=appointment.barber,
            appointment=appointment,
            overall_experience=overall_experience,
            review_text=review_text
        )

        for i in range(service_count):
            service_id = request.POST.get(f'service_{i}_id')
            service_stars = request.POST.get(f'service_{i}_stars')
            service_review_text = request.POST.get(f'service_{i}_text')
            ServiceReview.objects.create(
                review=review,
                service_id=service_id,
                stars=service_stars,
                review_text=service_review_text
            )

        # Mark the notification as read or delete it
        Notification.objects.filter(user=request.user, appointment=appointment).delete()

        return JsonResponse({'success': True, 'message': 'Review submitted successfully.'})
    except Appointment.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Appointment not found.'})

@login_required
def check_notifications(request):
    now = timezone.now()
    ended_appointments = Appointment.objects.filter(end_time__lte=now, customer=request.user, notified=False)
    notifications = []

    for appointment in ended_appointments:
        notifications.append({
            'id': appointment.id,
            'message': f'Your appointment with {appointment.barber.name} has ended. Please leave a review.'
        })
        appointment.notified = True
        appointment.save()

    # Clear notifications for deleted appointments
    # Assuming you have a Notification model
    Notification.objects.filter(user=request.user, appointment__isnull=True).delete()

    return JsonResponse({'notifications': notifications})