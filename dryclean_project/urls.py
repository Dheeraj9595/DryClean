"""
URL configuration for dryclean_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.documentation import include_docs_urls
from .views import root_view, health_check, api_overview

urlpatterns = [
    # Frontend URLs
    path('', include('frontend.urls')),
    
    # API URLs
    path('api/auth/', include('accounts.urls')),
    path('api/services/', include('services.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/docs/', include_docs_urls(title='Dry Cleaning API', public=True)),
    
    # Admin and utility URLs
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('api-overview/', api_overview, name='api_overview'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
