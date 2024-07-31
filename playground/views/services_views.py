from django.shortcuts import render, get_object_or_404
from playground.models import Service

def list_services(request):
    services = Service.objects.all()
    return render(request, 'services/list.html', {'services': services})

def service_detail(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    return render(request, 'services/detail.html', {'service': service})
