from django.urls import path, include
from . import views

urlpatterns = [
    # Registration
    path('register/', views.role_selection_view, name='register_page'),  # More general
    path('register/barber/', views.barber_register, name='barber_register'),  # More specific
    path('register/customer/', views.customer_register, name='customer_register'),  # More specific
    path('role-selection/', views.role_selection_view, name='role_selection_view'),  # More general

    # Login URLs 
    path('barber/login/', views.barber_login_view, name='barber_login'),  # Specific
    path('customer/login/', views.customer_login_view, name='customer_login'),  # Specific

    #Logout URLs
    path('customer/logout/', views.logout_user, name='logout_customer'),  # Specific
    path('barber/logout/', views.logout_user, name='logout_barber'),  # Specific

    # After customer has logged in
    path('customer_dashboard/', views.dashboard, name='customer_dashboard'),  # General
    path('customer_explore/', views.explore, name='customer_explore'),  # General
    path('customer_appointments/', views.appointments, name='customer_appointments'),  # General
    path('customer_profile/', views.profile, name='customer_profile'),  # General
    path('customer_profile/update/', views.update_customer, name='update_customer'),  # New URL for updating customer details

    #After barber has logged in
    path('barber/dashboard/', views.barber_dashboard, name='barber_dashboard'),
    path('barber/appointments/', views.barber_appointments, name='barber_appointments'),
    
    path('barber/reports/', views.barber_reports, name='barber_reports'),
    path('barber/profile/', views.barber_profile, name='barber_profile'),
    path('barber/settings/', views.barber_settings, name='barber_settings'),
    
    path('barber/manage_availability/', views.manage_availability, name='manage_availability'),
    path('get_availability/', views.get_availability, name='get_availability'),
    path('set_availability/', views.set_availability, name='set_availability'),
   

    path('barber/update/', views.update_barber, name='update_barber'),

    path('accounts/', include('django.contrib.auth.urls')),
    # Catch-all or dynamic URL pattern (should be placed at the end)
    # path('<str:slug>/', views.dynamic_page, name='dynamic_page'),  # Catch-all
]