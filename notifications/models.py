from django.db import models
from django.contrib.auth.models import User
from orders.models import Order


class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='notifications', blank=True, null=True)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Delivery information
    sent_at = models.DateTimeField(blank=True, null=True)
    delivery_status = models.CharField(max_length=100, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Metadata
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.notification_type} - {self.title} - {self.user.username}"
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']


class EmailTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"


class SMSTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "SMS Template"
        verbose_name_plural = "SMS Templates"


class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email preferences
    email_order_confirmation = models.BooleanField(default=True)
    email_status_updates = models.BooleanField(default=True)
    email_pickup_reminder = models.BooleanField(default=True)
    email_delivery_notification = models.BooleanField(default=True)
    email_promotional = models.BooleanField(default=False)
    
    # SMS preferences
    sms_order_confirmation = models.BooleanField(default=True)
    sms_status_updates = models.BooleanField(default=True)
    sms_pickup_reminder = models.BooleanField(default=True)
    sms_delivery_notification = models.BooleanField(default=True)
    sms_promotional = models.BooleanField(default=False)
    
    # Push notification preferences
    push_order_confirmation = models.BooleanField(default=True)
    push_status_updates = models.BooleanField(default=True)
    push_pickup_reminder = models.BooleanField(default=True)
    push_delivery_notification = models.BooleanField(default=True)
    push_promotional = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification Preferences - {self.user.username}"
    
    class Meta:
        verbose_name = "Notification Preference"
        verbose_name_plural = "Notification Preferences"


class NotificationLog(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=50)  # e.g., 'sent', 'failed', 'retry'
    details = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.notification} - {self.action}"
    
    class Meta:
        verbose_name = "Notification Log"
        verbose_name_plural = "Notification Logs"
        ordering = ['-created_at']
