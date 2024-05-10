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
    path('customer/logout/', views.logout_customer, name='logout_customer'),  # Specific


    # After customer has logged in
    path('dashboard/', views.dashboard, name='dashboard'),  # General
    path('explore/', views.explore, name='explore'),  # General
    path('appointments/', views.appointments, name='appointments'),  # General
    path('profile/', views.profile, name='profile'),  # General

    #After barber has logged in
    path('barber/dashboard/', views.barber_dashboard, name='barber_dashboard'),

    path('accounts/', include('django.contrib.auth.urls')),
    # Catch-all or dynamic URL pattern (should be placed at the end)
    # path('<str:slug>/', views.dynamic_page, name='dynamic_page'),  # Catch-all
]