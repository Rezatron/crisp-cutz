from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),  # Home page URL
    path('register/', views.role_selection_view, name='register_page'),  # Registration page URL with a unique name
    path('register/barber/', views.barber_register, name='barber_register'),  # Barber registration URL
    path('register/customer/', views.customer_register, name='customer_register'),  # Customer registration URL
    path('role-selection/', views.role_selection_view, name='role_selection_view'),  # Update the URL pattern
    # Add other URLs here
]
