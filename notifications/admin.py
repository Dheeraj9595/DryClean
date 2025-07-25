from django.contrib import admin
from .models import Notification, EmailTemplate, SMSTemplate, NotificationPreference, NotificationLog


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'notification_type', 'title', 'status', 'is_read', 'created_at')
    list_filter = ('notification_type', 'status', 'is_read', 'created_at')
    search_fields = ('user__username', 'user__email', 'title', 'message')
    readonly_fields = ('sent_at', 'delivery_status', 'error_message', 'created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'order')
        }),
        ('Notification Information', {
            'fields': ('notification_type', 'title', 'message', 'status')
        }),
        ('Delivery Information', {
            'fields': ('sent_at', 'delivery_status', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('is_read',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_sent', 'mark_as_failed', 'mark_as_read', 'mark_as_unread']
    
    def mark_as_sent(self, request, queryset):
        for notification in queryset:
            if notification.status == 'pending':
                notification.status = 'sent'
                notification.save()
        self.message_user(request, f"{queryset.count()} notifications marked as sent.")
    mark_as_sent.short_description = "Mark selected notifications as sent"
    
    def mark_as_failed(self, request, queryset):
        for notification in queryset:
            if notification.status == 'pending':
                notification.status = 'failed'
                notification.save()
        self.message_user(request, f"{queryset.count()} notifications marked as failed.")
    mark_as_failed.short_description = "Mark selected notifications as failed"
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} notifications marked as read.")
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f"{queryset.count()} notifications marked as unread.")
    mark_as_unread.short_description = "Mark selected notifications as unread"


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'subject', 'body')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'subject', 'body')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SMSTemplate)
class SMSTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'message_preview', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'message')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'message')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_order_confirmation', 'sms_order_confirmation', 'created_at')
    list_filter = ('email_order_confirmation', 'sms_order_confirmation', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Email Preferences', {
            'fields': (
                'email_order_confirmation', 'email_status_updates', 'email_pickup_reminder',
                'email_delivery_notification', 'email_promotional'
            )
        }),
        ('SMS Preferences', {
            'fields': (
                'sms_order_confirmation', 'sms_status_updates', 'sms_pickup_reminder',
                'sms_delivery_notification', 'sms_promotional'
            )
        }),
        ('Push Notification Preferences', {
            'fields': (
                'push_order_confirmation', 'push_status_updates', 'push_pickup_reminder',
                'push_delivery_notification', 'push_promotional'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('notification', 'action', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('notification__title', 'notification__user__username')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Log Information', {
            'fields': ('notification', 'action', 'details')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
