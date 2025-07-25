from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # User endpoints
    path('', views.NotificationListView.as_view(), name='notification_list'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification_detail'),
    path('mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('stats/', views.notification_stats, name='notification_stats'),
    path('preferences/', views.NotificationPreferenceView.as_view(), name='notification_preferences'),
    
    # Admin endpoints
    path('admin/', views.AdminNotificationListView.as_view(), name='admin_notification_list'),
    path('admin/<int:pk>/', views.AdminNotificationDetailView.as_view(), name='admin_notification_detail'),
    path('admin/send/', views.send_notification, name='send_notification'),
    path('admin/send-bulk/', views.send_bulk_notification, name='send_bulk_notification'),
    path('admin/test/', views.test_notification, name='test_notification'),
    path('admin/stats/', views.admin_notification_stats, name='admin_notification_stats'),
    
    # Template management
    path('admin/email-templates/', views.EmailTemplateListView.as_view(), name='email_template_list'),
    path('admin/email-templates/<int:pk>/', views.EmailTemplateDetailView.as_view(), name='email_template_detail'),
    path('admin/sms-templates/', views.SMSTemplateListView.as_view(), name='sms_template_list'),
    path('admin/sms-templates/<int:pk>/', views.SMSTemplateDetailView.as_view(), name='sms_template_detail'),
] 