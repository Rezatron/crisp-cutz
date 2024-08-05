# urls.py
from django.urls import path
from .views.common_views import home_page, role_selection_view, logout_user, list_customers
from .views.customer_views import (
    customer_register, customer_login_view, dashboard, explore, appointments, profile, update_customer
)
from .views.barber_views import (
    barber_register, barber_login_view, barber_dashboard, barber_appointments, barber_reports, barber_profile, update_barber, barber_settings, manage_availability, get_availability, set_availability, delete_availability, get_availability_for_date, manage_services, create_service)
from .views.services_views import get_services_by_barber
from .views.appointment_views import create_appointment, appointment_confirmation, appointment_list, appointment_detail

urlpatterns = [
    path('', home_page, name='home'),
    path('register/', role_selection_view, name='role_selection'),
    path('logout/', logout_user, name='logout'),
    path('logout/barber/', logout_user, name='logout_barber'),
    path('logout/customer/', logout_user, name='logout_customer'),
    path('customer/register/', customer_register, name='customer_register'),
    path('customer/login/', customer_login_view, name='customer_login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('explore/', explore, name='customer_explore'),
    path('appointments/', appointments, name='customer_appointments'),
    path('profile/', profile, name='customer_profile'),
    path('profile/update/', update_customer, name='update_customer'),
    path('barber/register/', barber_register, name='barber_register'),
    path('barber/login/', barber_login_view, name='barber_login'),
    path('barber/dashboard/', barber_dashboard, name='barber_dashboard'),
    path('barber/appointments/', barber_appointments, name='barber_appointments'),
    path('barber/reports/', barber_reports, name='barber_reports'),
    path('barber/profile/', barber_profile, name='barber_profile'),
    path('barber/profile/update/', update_barber, name='update_barber'),
    path('create-service/', create_service, name='create_service'),
    path('manage-services/', manage_services, name='manage_services'),

    path('barber/settings/', barber_settings, name='barber_settings'),
    path('barber/availability/', manage_availability, name='manage_availability'),
    path('barber/availability/get/', get_availability, name='get_availability'),
    path('barber/availability/set/', set_availability, name='set_availability'),
    path('barber/availability/delete/', delete_availability, name='delete_availability'),
    path('barber/availability/date/', get_availability_for_date, name='get_availability_for_date'),

    path('customers/', list_customers, name='list_customers'),
    path('appointments/create/', create_appointment, name='create_appointment'),
    path('appointments/create/<int:barber_id>/', create_appointment, name='create_appointment_with_barber'),
    path('appointments/<int:appointment_id>/confirmation/', appointment_confirmation, name='appointment_confirmation'),  # Include appointment_id for confirmation
    path('get-services-by-barber/', get_services_by_barber, name='get_services_by_barber'),
    path('appointments/', appointment_list, name='appointment_list'),
    path('appointments/<int:appointment_id>/', appointment_detail, name='appointment_detail'),
]
