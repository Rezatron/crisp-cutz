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
    logger.debug("submit_review called")
    appointment_id = request.POST.get('appointment_id')
    overall_experience = request.POST.get('overall_experience')
    review_text = request.POST.get('review_text')
    service_count = request.POST.get('service_count')

    logger.debug(f"Received data: appointment_id={appointment_id}, overall_experience={overall_experience}, review_text={review_text}, service_count={service_count}")

    if service_count is not None:
        try:
            service_count = int(service_count)
        except ValueError:
            logger.error("Invalid service_count value")
            return JsonResponse({'success': False, 'message': 'Invalid service count.'})
    else:
        logger.error("service_count is missing")
        return JsonResponse({'success': False, 'message': 'Service count is required.'})

    try:
        appointment = Appointment.objects.get(id=appointment_id, user=request.user)
        logger.debug(f"Appointment found: {appointment}")
        review = Review.objects.create(
            user=request.user,
            barber=appointment.barber,
            appointment=appointment,
            overall_experience=overall_experience,
            review_text=review_text
        )
        logger.debug(f"Review created: {review}")

        for i in range(service_count):
            service_id = request.POST.get(f'service_{i}_id')
            service_stars = request.POST.get(f'service_{i}_stars')
            service_review_text = request.POST.get(f'service_{i}_text')

            logger.debug(f"Service {i}: service_id={service_id}, service_stars={service_stars}, service_review_text={service_review_text}")

            if not service_id or not service_stars:
                logger.warning(f"Skipping service {i} due to missing data: service_id={service_id}, service_stars={service_stars}")
                continue

            try:
                service_stars = float(service_stars)
            except ValueError:
                logger.error(f"Invalid star rating for service {i}")
                return JsonResponse({'success': False, 'message': 'Invalid star rating.'})

            ServiceReview.objects.create(
                review=review,
                service_id=service_id,
                stars=service_stars,
                review_text=service_review_text
            )
            logger.debug(f"ServiceReview created for service {i}")

        Notification.objects.filter(user=request.user, appointment=appointment).delete()
        logger.debug("Notifications deleted")

        return JsonResponse({'success': True, 'message': 'Review submitted successfully.'})
    except Appointment.DoesNotExist:
        logger.error("Appointment not found")
        return JsonResponse({'success': False, 'message': 'Appointment not found.'})
    except Exception as e:
        logger.exception("An unexpected error occurred")
        return JsonResponse({'success': False, 'message': 'An unexpected error occurred.'})

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

    Notification.objects.filter(user=request.user, appointment__isnull=True).delete()

    return JsonResponse({'notifications': notifications})