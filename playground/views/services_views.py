from django.shortcuts import render, get_object_or_404
from playground.models import Service
from django.http import JsonResponse
from playground.models import BarberService

def list_services(request):
    services = Service.objects.all()
    return render(request, 'services/list.html', {'services': services})

def service_detail(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    return render(request, 'services/detail.html', {'service': service})

def get_services_by_barber(request):
    barber_id = request.GET.get('barber_id')
    barber_services = BarberService.objects.filter(barber_id=barber_id)
    services_data = [
        {
            'id': service.id,
            'name': service.service.name,
            'price': service.price,
            'duration': str(service.duration)  # Convert duration to string
        }
        for service in barber_services
    ]
    # Print debug information to the server console
    print("Services Data:", services_data)
    return JsonResponse(services_data, safe=False)