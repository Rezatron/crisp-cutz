from django.urls import path, include
from . import views

urlpatterns = [
    # Registration
    path('register/', views.role_selection_view, name='register_page'),
    path('register/barber/', views.barber_register, name='barber_register'),
    path('register/customer/', views.customer_register, name='customer_register'),
    path('role-selection/', views.role_selection_view, name='role_selection_view'),

    # Login URLs
    path('barber/login/', views.barber_login_view, name='barber_login'),
    path('customer/login/', views.customer_login_view, name='customer_login'),

    # Logout URLs
    path('customer/logout/', views.logout_user, name='logout_customer'),
    path('barber/logout/', views.logout_user, name='logout_barber'),

    # After customer has logged in
    path('customer_dashboard/', views.dashboard, name='customer_dashboard'),
    path('customer_explore/', views.explore, name='customer_explore'),
    path('customer_appointments/', views.appointments, name='customer_appointments'),
    path('customer_profile/', views.profile, name='customer_profile'),
    path('customer_profile/update/', views.update_customer, name='update_customer'),

    # After barber has logged in
    path('barber/dashboard/', views.barber_dashboard, name='barber_dashboard'),
    path('barber/appointments/', views.barber_appointments, name='barber_appointments'),
    path('barber/reports/', views.barber_reports, name='barber_reports'),
    path('barber/profile/', views.barber_profile, name='barber_profile'),
    path('barber/settings/', views.barber_settings, name='barber_settings'),
    path('barber/manage_availability/', views.manage_availability, name='manage_availability'),
    path('get_availability/', views.get_availability, name='get_availability'),
    path('set_availability/', views.set_availability, name='set_availability'),

    # Add the following two URL patterns:
    path('get_availability_for_date/', views.get_availability_for_date, name='get_availability_for_date'),
    path('delete_availability/', views.delete_availability, name='delete_availability'),

    path('barber/update/', views.update_barber, name='update_barber'),
    path('accounts/', include('django.contrib.auth.urls')),
]
