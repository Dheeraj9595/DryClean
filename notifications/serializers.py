from rest_framework import serializers
from .models import Notification, EmailTemplate, SMSTemplate, NotificationPreference, NotificationLog


class NotificationSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    customer_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'customer_name', 'order', 'order_number', 'notification_type',
            'title', 'message', 'status', 'sent_at', 'delivery_status', 'error_message',
            'is_read', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'customer_name', 'order_number', 'status', 'sent_at', 'delivery_status',
            'error_message', 'created_at', 'updated_at'
        ]


class NotificationListSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'status', 'is_read', 'order_number', 'created_at'
        ]
        read_only_fields = ['id', 'order_number', 'created_at']


class MarkNotificationReadSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    
    def validate_notification_ids(self, value):
        user = self.context['request'].user
        valid_notifications = Notification.objects.filter(
            id__in=value,
            user=user
        ).values_list('id', flat=True)
        
        if len(valid_notifications) != len(value):
            raise serializers.ValidationError("Some notification IDs are invalid or don't belong to you.")
        
        return value


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'subject', 'body', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SMSTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSTemplate
        fields = [
            'id', 'name', 'message', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'email_order_confirmation', 'email_status_updates', 'email_pickup_reminder',
            'email_delivery_notification', 'email_promotional', 'sms_order_confirmation',
            'sms_status_updates', 'sms_pickup_reminder', 'sms_delivery_notification',
            'sms_promotional', 'push_order_confirmation', 'push_status_updates',
            'push_pickup_reminder', 'push_delivery_notification', 'push_promotional',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationLogSerializer(serializers.ModelSerializer):
    notification_title = serializers.CharField(source='notification.title', read_only=True)
    
    class Meta:
        model = NotificationLog
        fields = [
            'id', 'notification', 'notification_title', 'action', 'details', 'created_at'
        ]
        read_only_fields = ['id', 'notification_title', 'created_at']


class SendNotificationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    notification_type = serializers.ChoiceField(choices=Notification.NOTIFICATION_TYPE_CHOICES)
    title = serializers.CharField(max_length=255)
    message = serializers.CharField()
    order_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_user_id(self, value):
        from django.contrib.auth.models import User
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        return value
    
    def validate_order_id(self, value):
        if value:
            from orders.models import Order
            try:
                Order.objects.get(id=value)
            except Order.DoesNotExist:
                raise serializers.ValidationError("Order not found.")
        return value


class BulkNotificationSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    notification_type = serializers.ChoiceField(choices=Notification.NOTIFICATION_TYPE_CHOICES)
    title = serializers.CharField(max_length=255)
    message = serializers.CharField()
    
    def validate_user_ids(self, value):
        from django.contrib.auth.models import User
        valid_users = User.objects.filter(id__in=value).values_list('id', flat=True)
        if len(valid_users) != len(value):
            raise serializers.ValidationError("Some user IDs are invalid.")
        return value


class NotificationStatsSerializer(serializers.Serializer):
    total_notifications = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()
    notifications_by_type = serializers.DictField()
    notifications_by_status = serializers.DictField()
    recent_notifications = NotificationListSerializer(many=True)


class TestNotificationSerializer(serializers.Serializer):
    notification_type = serializers.ChoiceField(choices=Notification.NOTIFICATION_TYPE_CHOICES)
    test_email = serializers.EmailField(required=False)
    test_phone = serializers.CharField(max_length=15, required=False)
    
    def validate(self, attrs):
        notification_type = attrs.get('notification_type')
        
        if notification_type == 'email' and not attrs.get('test_email'):
            raise serializers.ValidationError("Test email is required for email notifications.")
        
        if notification_type == 'sms' and not attrs.get('test_phone'):
            raise serializers.ValidationError("Test phone number is required for SMS notifications.")
        
        return attrs 