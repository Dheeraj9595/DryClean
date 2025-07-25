from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone
from .models import Notification, EmailTemplate, SMSTemplate, NotificationPreference, NotificationLog
from .serializers import (
    NotificationSerializer, NotificationListSerializer, MarkNotificationReadSerializer,
    EmailTemplateSerializer, SMSTemplateSerializer, NotificationPreferenceSerializer,
    SendNotificationSerializer, BulkNotificationSerializer, NotificationStatsSerializer,
    TestNotificationSerializer
)
from .tasks import send_email_notification


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            queryset = Notification.objects.all()
        else:
            queryset = Notification.objects.filter(user=user)
        
        # Apply filters
        notification_type = self.request.query_params.get('type')
        is_read = self.request.query_params.get('is_read')
        
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        return queryset.order_by('-created_at')


class NotificationDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Notification.objects.all()
        return Notification.objects.filter(user=user)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_read = True
        instance.save()
        return Response({'message': 'Notification marked as read.'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notifications_read(request):
    """Mark multiple notifications as read"""
    serializer = MarkNotificationReadSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        notification_ids = serializer.validated_data['notification_ids']
        Notification.objects.filter(id__in=notification_ids).update(is_read=True)
        
        return Response({
            'message': f'{len(notification_ids)} notifications marked as read.'
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_stats(request):
    """Get notification statistics for user"""
    user = request.user
    
    notifications = Notification.objects.filter(user=user)
    
    stats = {
        'total_notifications': notifications.count(),
        'unread_notifications': notifications.filter(is_read=False).count(),
        'notifications_by_type': notifications.values('notification_type').annotate(
            count=Count('id')
        ),
        'notifications_by_status': notifications.values('status').annotate(
            count=Count('id')
        ),
        'recent_notifications': NotificationListSerializer(
            notifications.order_by('-created_at')[:5], many=True
        ).data
    }
    
    return Response(stats)


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        preference, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preference


# Admin views for managing notifications
class AdminNotificationListView(generics.ListCreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = Notification.objects.all()
        
        # Apply filters
        user_id = self.request.query_params.get('user_id')
        notification_type = self.request.query_params.get('type')
        status_filter = self.request.query_params.get('status')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')


class AdminNotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAdminUser]


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def send_notification(request):
    """Send notification to a specific user"""
    serializer = SendNotificationSerializer(data=request.data)
    if serializer.is_valid():
        user_id = serializer.validated_data['user_id']
        notification_type = serializer.validated_data['notification_type']
        title = serializer.validated_data['title']
        message = serializer.validated_data['message']
        order_id = serializer.validated_data.get('order_id')
        
        from django.contrib.auth.models import User
        user = User.objects.get(id=user_id)
        
        # Create notification record
        notification = Notification.objects.create(
            user=user,
            order_id=order_id,
            notification_type=notification_type,
            title=title,
            message=message,
            status='pending'
        )
        
        # Send notification based on type
        if notification_type == 'email':
            send_email_notification.delay(notification.id)
        elif notification_type == 'sms':
            # send_sms_notification.delay(notification.id)  # SMS functionality not implemented yet
            pass
        
        return Response({
            'message': 'Notification sent successfully.',
            'notification_id': notification.id
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def send_bulk_notification(request):
    """Send notification to multiple users"""
    serializer = BulkNotificationSerializer(data=request.data)
    if serializer.is_valid():
        user_ids = serializer.validated_data['user_ids']
        notification_type = serializer.validated_data['notification_type']
        title = serializer.validated_data['title']
        message = serializer.validated_data['message']
        
        from django.contrib.auth.models import User
        users = User.objects.filter(id__in=user_ids)
        
        notifications_created = 0
        
        for user in users:
            # Check user preferences
            preference, created = NotificationPreference.objects.get_or_create(user=user)
            
            should_send = False
            if notification_type == 'email':
                should_send = getattr(preference, f'email_{title.lower().replace(" ", "_")}', True)
            elif notification_type == 'sms':
                should_send = getattr(preference, f'sms_{title.lower().replace(" ", "_")}', True)
            
            if should_send:
                notification = Notification.objects.create(
                    user=user,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    status='pending'
                )
                
                # Send notification
                if notification_type == 'email':
                    send_email_notification.delay(notification.id)
                elif notification_type == 'sms':
                    # send_sms_notification.delay(notification.id)  # SMS functionality not implemented yet
                    pass
                
                notifications_created += 1
        
        return Response({
            'message': f'{notifications_created} notifications sent successfully.',
            'total_users': len(users),
            'notifications_sent': notifications_created
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def test_notification(request):
    """Test notification sending"""
    serializer = TestNotificationSerializer(data=request.data)
    if serializer.is_valid():
        notification_type = serializer.validated_data['notification_type']
        test_email = serializer.validated_data.get('test_email')
        test_phone = serializer.validated_data.get('test_phone')
        
        if notification_type == 'email' and test_email:
            # Test email sending
            try:
                send_email_notification.delay(
                    notification_id=None,
                    test_email=test_email,
                    test_message="This is a test notification from Saarvin Dry Clean."
                )
                return Response({
                    'message': 'Test email sent successfully.'
                })
            except Exception as e:
                return Response({
                    'error': 'Failed to send test email.',
                    'details': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        elif notification_type == 'sms' and test_phone:
            # Test SMS sending
            try:
                # send_sms_notification.delay(
                #     notification_id=None,
                #     test_phone=test_phone,
                #     test_message="This is a test SMS from Saarvin Dry Clean."
                # )  # SMS functionality not implemented yet
                return Response({
                    'message': 'SMS functionality not implemented yet.'
                })
            except Exception as e:
                return Response({
                    'error': 'Failed to send test SMS.',
                    'details': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Email and SMS template management
class EmailTemplateListView(generics.ListCreateAPIView):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAdminUser]


class EmailTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAdminUser]


class SMSTemplateListView(generics.ListCreateAPIView):
    queryset = SMSTemplate.objects.all()
    serializer_class = SMSTemplateSerializer
    permission_classes = [permissions.IsAdminUser]


class SMSTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SMSTemplate.objects.all()
    serializer_class = SMSTemplateSerializer
    permission_classes = [permissions.IsAdminUser]


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_notification_stats(request):
    """Get admin notification statistics"""
    today = timezone.now().date()
    last_week = today - timezone.timedelta(days=7)
    
    # Notification statistics
    total_notifications = Notification.objects.count()
    today_notifications = Notification.objects.filter(created_at__date=today).count()
    week_notifications = Notification.objects.filter(created_at__date__gte=last_week).count()
    
    # Status breakdown
    status_counts = Notification.objects.values('status').annotate(count=Count('id'))
    status_breakdown = {item['status']: item['count'] for item in status_counts}
    
    # Type breakdown
    type_counts = Notification.objects.values('notification_type').annotate(count=Count('id'))
    type_breakdown = {item['notification_type']: item['count'] for item in type_counts}
    
    # Recent notifications
    recent_notifications = Notification.objects.select_related('user').order_by('-created_at')[:10]
    
    stats = {
        'total_notifications': total_notifications,
        'today_notifications': today_notifications,
        'week_notifications': week_notifications,
        'status_breakdown': status_breakdown,
        'type_breakdown': type_breakdown,
        'recent_notifications': NotificationListSerializer(recent_notifications, many=True).data
    }
    
    return Response(stats)
