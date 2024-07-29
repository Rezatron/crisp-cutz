"""
CRISPCUT URL!!
URL configuration for crispcutz project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView
from playground.views.common_views import home_page, logout_user
from playground.views.customer_views import dashboard
from playground.views.barber_views import barber_dashboard
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', home_page, name='home'),  # Home page
    path('admin/', admin.site.urls),
    path('register/', include('playground.urls')),  # Include playground URLs for role selection and more
    path('login/', LoginView.as_view(), name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('barber/dashboard/', barber_dashboard, name='barber_dashboard'),
    path('logout/', logout_user, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
