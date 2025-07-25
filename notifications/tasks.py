from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, EmailTemplate

@shared_task
def send_order_notification(order_id, notification_type):
    """
    Send notification for order status changes
    """
    try:
        from orders.models import Order
        order = Order.objects.get(id=order_id)
        
        # Create notification record
        notification = Notification.objects.create(
            recipient=order.customer,
            type=notification_type,
            title=f"Order {order.order_number} Update",
            message=f"Your order status has been updated to {order.get_status_display()}"
        )
        
        # Send email notification
        if notification_type == 'email':
            send_email_notification.delay(notification.id)
        
        return True
    except Exception as e:
        print(f"Error sending notification: {e}")
        return False

@shared_task
def send_email_notification(notification_id):
    """
    Send email notification
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        
        send_mail(
            subject=notification.title,
            message=notification.message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[notification.recipient.email],
            fail_silently=False,
        )
        
        notification.is_sent = True
        notification.save()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False 