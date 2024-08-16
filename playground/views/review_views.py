from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from ..models import Appointment, Review, ServiceReview
from ..forms import ReviewForm, ServiceReviewForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone

@login_required
def fetch_appointment_details(request, appointment_id):
    if request.method == 'GET':
        appointment = get_object_or_404(Appointment, id=appointment_id)
        data = {
            'success': True,
            'appointment_id': appointment.id,
            'barber': appointment.barber.name,
            'services': [{'id': service.id, 'name': service.name} for service in appointment.services.all()],
        }
        return JsonResponse(data)
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def submit_review(request):
    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        service_review_forms = [ServiceReviewForm(request.POST, prefix=f'service_{i}') for i in range(int(request.POST.get('service_count', 0)))]
        
        if review_form.is_valid() and all(form.is_valid() for form in service_review_forms):
            review = review_form.save()
            for form in service_review_forms:
                service_review = form.save(commit=False)
                service_review.review = review
                service_review.save()
            return JsonResponse({'success': True, 'message': 'Review submitted successfully!'})
        else:
            errors = review_form.errors.as_json()
            for form in service_review_forms:
                errors.update(form.errors.as_json())
            return JsonResponse({'success': False, 'errors': errors})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


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

    return JsonResponse({'notifications': notifications})
