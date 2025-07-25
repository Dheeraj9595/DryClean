from django.shortcuts import render
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Order, OrderItem, OrderStatusHistory, PickupSchedule, DeliverySchedule
from .serializers import (
    OrderSerializer, CreateOrderSerializer, OrderListSerializer,
    UpdateOrderStatusSerializer, OrderFilterSerializer, OrderItemSerializer,
    PickupScheduleSerializer, DeliveryScheduleSerializer
)
from notifications.tasks import send_order_notification


class OrderListView(generics.ListCreateAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            # Admin can see all orders
            queryset = Order.objects.all()
        else:
            # Regular users can only see their own orders
            queryset = Order.objects.filter(customer=user)
        
        # Apply filters
        status_filter = self.request.query_params.get('status')
        order_type = self.request.query_params.get('order_type')
        payment_status = self.request.query_params.get('payment_status')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if order_type:
            queryset = queryset.filter(order_type=order_type)
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderListSerializer


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer=user)


class UpdateOrderStatusView(generics.UpdateAPIView):
    serializer_class = UpdateOrderStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer=user)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        old_status = instance.status
        updated_order = serializer.save()
        
        # Send notification for status change
        if old_status != updated_order.status:
            send_order_notification.delay(
                user_id=updated_order.customer.id,
                order_id=updated_order.id,
                notification_type='status_update',
                title=f'Order Status Updated',
                message=f'Your order {updated_order.order_number} status has been updated to {updated_order.get_status_display()}'
            )
        
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def order_tracking(request, order_id):
    """Get detailed tracking information for an order"""
    try:
        user = request.user
        if user.is_staff:
            order = Order.objects.get(id=order_id)
        else:
            order = Order.objects.get(id=order_id, customer=user)
        
        # Get status history
        status_history = order.status_history.order_by('-created_at')
        
        # Get pickup and delivery schedules
        pickup_schedule = getattr(order, 'pickup_schedule', None)
        delivery_schedule = getattr(order, 'delivery_schedule', None)
        
        tracking_data = {
            'order': {
                'id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'status_display': order.get_status_display(),
                'created_at': order.created_at,
                'estimated_completion': order.estimated_completion,
            },
            'status_history': [
                {
                    'status': history.status,
                    'status_display': history.get_status_display(),
                    'notes': history.notes,
                    'updated_by': history.updated_by.get_full_name() if history.updated_by else 'System',
                    'created_at': history.created_at,
                }
                for history in status_history
            ],
            'pickup_schedule': PickupScheduleSerializer(pickup_schedule).data if pickup_schedule else None,
            'delivery_schedule': DeliveryScheduleSerializer(delivery_schedule).data if delivery_schedule else None,
        }
        
        return Response(tracking_data)
        
    except Order.DoesNotExist:
        return Response({
            'error': 'Order not found.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def order_history(request):
    """Get user's order history with statistics"""
    user = request.user
    
    # Get all orders for the user
    orders = Order.objects.filter(customer=user).order_by('-created_at')
    
    # Calculate statistics
    total_orders = orders.count()
    total_spent = orders.filter(payment_status='paid').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    status_counts = orders.values('status').annotate(count=Count('id'))
    status_stats = {item['status']: item['count'] for item in status_counts}
    
    # Get recent orders
    recent_orders = orders[:10]
    
    history_data = {
        'statistics': {
            'total_orders': total_orders,
            'total_spent': total_spent,
            'status_breakdown': status_stats,
        },
        'recent_orders': OrderListSerializer(recent_orders, many=True).data
    }
    
    return Response(history_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_order(request, order_id):
    """Cancel an order"""
    try:
        user = request.user
        if user.is_staff:
            order = Order.objects.get(id=order_id)
        else:
            order = Order.objects.get(id=order_id, customer=user)
        
        # Check if order can be cancelled
        if order.status in ['delivered', 'cancelled']:
            return Response({
                'error': 'Order cannot be cancelled.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update order status
        order.status = 'cancelled'
        order.save()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status='cancelled',
            notes='Order cancelled by customer' if not user.is_staff else 'Order cancelled by admin',
            updated_by=user
        )
        
        # Send notification
        send_order_notification.delay(
            user_id=order.customer.id,
            order_id=order.id,
            notification_type='status_update',
            title='Order Cancelled',
            message=f'Your order {order.order_number} has been cancelled.'
        )
        
        return Response({
            'message': 'Order cancelled successfully.'
        })
        
    except Order.DoesNotExist:
        return Response({
            'error': 'Order not found.'
        }, status=status.HTTP_404_NOT_FOUND)


# Admin views
class AdminOrderListView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = Order.objects.all()
        
        # Apply filters
        status_filter = self.request.query_params.get('status')
        order_type = self.request.query_params.get('order_type')
        payment_status = self.request.query_params.get('payment_status')
        customer_id = self.request.query_params.get('customer_id')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if order_type:
            queryset = queryset.filter(order_type=order_type)
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        return queryset.order_by('-created_at')


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_dashboard(request):
    """Admin dashboard with order statistics"""
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)
    
    # Order statistics
    total_orders = Order.objects.count()
    today_orders = Order.objects.filter(created_at__date=today).count()
    week_orders = Order.objects.filter(created_at__date__gte=last_week).count()
    month_orders = Order.objects.filter(created_at__date__gte=last_month).count()
    
    # Revenue statistics
    total_revenue = Order.objects.filter(payment_status='paid').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    today_revenue = Order.objects.filter(
        created_at__date=today,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    week_revenue = Order.objects.filter(
        created_at__date__gte=last_week,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    month_revenue = Order.objects.filter(
        created_at__date__gte=last_month,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Status breakdown
    status_counts = Order.objects.values('status').annotate(count=Count('id'))
    status_breakdown = {item['status']: item['count'] for item in status_counts}
    
    # Recent orders
    recent_orders = Order.objects.select_related('customer').order_by('-created_at')[:10]
    
    # Pending actions
    pending_pickups = PickupSchedule.objects.filter(
        is_completed=False,
        scheduled_date__gte=today
    ).count()
    
    pending_deliveries = DeliverySchedule.objects.filter(
        is_completed=False,
        scheduled_date__gte=today
    ).count()
    
    dashboard_data = {
        'statistics': {
            'orders': {
                'total': total_orders,
                'today': today_orders,
                'week': week_orders,
                'month': month_orders,
            },
            'revenue': {
                'total': total_revenue,
                'today': today_revenue,
                'week': week_revenue,
                'month': month_revenue,
            },
            'status_breakdown': status_breakdown,
            'pending_actions': {
                'pickups': pending_pickups,
                'deliveries': pending_deliveries,
            }
        },
        'recent_orders': OrderListSerializer(recent_orders, many=True).data
    }
    
    return Response(dashboard_data)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def assign_pickup_agent(request, order_id):
    """Assign pickup agent to an order"""
    try:
        order = Order.objects.get(id=order_id)
        agent_id = request.data.get('agent_id')
        
        if not agent_id:
            return Response({
                'error': 'Agent ID is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from django.contrib.auth.models import User
        try:
            agent = User.objects.get(id=agent_id, is_staff=True)
        except User.DoesNotExist:
            return Response({
                'error': 'Agent not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create or update pickup schedule
        pickup_schedule, created = PickupSchedule.objects.get_or_create(
            order=order,
            defaults={
                'scheduled_date': order.pickup_date,
                'scheduled_time_slot': order.pickup_time_slot,
                'pickup_agent': agent,
            }
        )
        
        if not created:
            pickup_schedule.pickup_agent = agent
            pickup_schedule.save()
        
        return Response({
            'message': 'Pickup agent assigned successfully.'
        })
        
    except Order.DoesNotExist:
        return Response({
            'error': 'Order not found.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def assign_delivery_agent(request, order_id):
    """Assign delivery agent to an order"""
    try:
        order = Order.objects.get(id=order_id)
        agent_id = request.data.get('agent_id')
        
        if not agent_id:
            return Response({
                'error': 'Agent ID is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from django.contrib.auth.models import User
        try:
            agent = User.objects.get(id=agent_id, is_staff=True)
        except User.DoesNotExist:
            return Response({
                'error': 'Agent not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create or update delivery schedule
        delivery_schedule, created = DeliverySchedule.objects.get_or_create(
            order=order,
            defaults={
                'scheduled_date': order.delivery_date or order.pickup_date + timedelta(days=2),
                'scheduled_time_slot': order.delivery_time_slot or '9:00 AM - 12:00 PM',
                'delivery_agent': agent,
            }
        )
        
        if not created:
            delivery_schedule.delivery_agent = agent
            delivery_schedule.save()
        
        return Response({
            'message': 'Delivery agent assigned successfully.'
        })
        
    except Order.DoesNotExist:
        return Response({
            'error': 'Order not found.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def agent_assignments(request):
    """Get agent assignments for today"""
    today = timezone.now().date()
    
    pickup_assignments = PickupSchedule.objects.filter(
        scheduled_date=today,
        is_completed=False
    ).select_related('order', 'pickup_agent')
    
    delivery_assignments = DeliverySchedule.objects.filter(
        scheduled_date=today,
        is_completed=False
    ).select_related('order', 'delivery_agent')
    
    assignments_data = {
        'pickup_assignments': [
            {
                'id': assignment.id,
                'order_number': assignment.order.order_number,
                'customer_name': assignment.order.customer.get_full_name(),
                'address': assignment.order.pickup_address,
                'time_slot': assignment.scheduled_time_slot,
                'agent_name': assignment.pickup_agent.get_full_name() if assignment.pickup_agent else None,
                'is_completed': assignment.is_completed,
            }
            for assignment in pickup_assignments
        ],
        'delivery_assignments': [
            {
                'id': assignment.id,
                'order_number': assignment.order.order_number,
                'customer_name': assignment.order.customer.get_full_name(),
                'address': assignment.order.delivery_address or assignment.order.pickup_address,
                'time_slot': assignment.scheduled_time_slot,
                'agent_name': assignment.delivery_agent.get_full_name() if assignment.delivery_agent else None,
                'is_completed': assignment.is_completed,
            }
            for assignment in delivery_assignments
        ]
    }
    
    return Response(assignments_data)
