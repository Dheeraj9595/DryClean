from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('services/', views.services, name='services'),
    path('pricing/', views.pricing, name='pricing'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Protected pages
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('orders/', views.orders, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('create-order/', views.create_order, name='create_order'),
    path('notifications/', views.notifications, name='notifications'),
] 