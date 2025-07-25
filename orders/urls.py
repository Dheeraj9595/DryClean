from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Customer endpoints
    path('', views.OrderListView.as_view(), name='order_list'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/status/', views.UpdateOrderStatusView.as_view(), name='update_status'),
    path('<int:order_id>/tracking/', views.order_tracking, name='order_tracking'),
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('history/', views.order_history, name='order_history'),
    
    # Admin endpoints
    path('admin/', views.AdminOrderListView.as_view(), name='admin_order_list'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/<int:order_id>/assign-pickup/', views.assign_pickup_agent, name='assign_pickup_agent'),
    path('admin/<int:order_id>/assign-delivery/', views.assign_delivery_agent, name='assign_delivery_agent'),
    path('admin/assignments/', views.agent_assignments, name='agent_assignments'),
] 