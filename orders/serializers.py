from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Order, OrderItem, OrderStatusHistory, PickupSchedule, DeliverySchedule
from services.models import Service, ServiceVariant
from accounts.serializers import UserSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True)
    category_name = serializers.CharField(source='service.category.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'service', 'service_name', 'variant', 'variant_name', 'category_name',
            'quantity', 'unit_price', 'total_price', 'description', 'special_instructions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'unit_price', 'total_price', 'created_at', 'updated_at']


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True)
    
    class Meta:
        model = OrderStatusHistory
        fields = [
            'id', 'order', 'status', 'notes', 'updated_by', 'updated_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PickupScheduleSerializer(serializers.ModelSerializer):
    pickup_agent_name = serializers.CharField(source='pickup_agent.get_full_name', read_only=True)
    
    class Meta:
        model = PickupSchedule
        fields = [
            'id', 'order', 'scheduled_date', 'scheduled_time_slot', 'actual_pickup_time',
            'pickup_agent', 'pickup_agent_name', 'notes', 'is_completed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DeliveryScheduleSerializer(serializers.ModelSerializer):
    delivery_agent_name = serializers.CharField(source='delivery_agent.get_full_name', read_only=True)
    
    class Meta:
        model = DeliverySchedule
        fields = [
            'id', 'order', 'scheduled_date', 'scheduled_time_slot', 'actual_delivery_time',
            'delivery_agent', 'delivery_agent_name', 'notes', 'is_completed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OrderSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    pickup_schedule = PickupScheduleSerializer(read_only=True)
    delivery_schedule = DeliveryScheduleSerializer(read_only=True)
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'order_number', 'status', 'order_type',
            'pickup_address', 'pickup_date', 'pickup_time_slot',
            'delivery_address', 'delivery_date', 'delivery_time_slot',
            'subtotal', 'tax', 'delivery_fee', 'total_amount',
            'payment_status', 'payment_method', 'special_instructions',
            'estimated_completion', 'items', 'status_history',
            'pickup_schedule', 'delivery_schedule', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'subtotal', 'tax', 'delivery_fee', 'created_at', 'updated_at'
        ]
    
    def get_total_amount(self, obj):
        """Calculate total amount dynamically from order items"""
        try:
            # Calculate subtotal from order items
            subtotal = sum(item.total_price for item in obj.items.all())
            
            # Calculate tax (5% GST)
            tax = subtotal * 0.05
            
            # Calculate delivery fee (free for orders above ₹500, else ₹50)
            delivery_fee = 0 if subtotal >= 500 else 50
            
            # Calculate total
            total = subtotal + tax + delivery_fee
            
            return total
        except Exception:
            # Fallback to stored value if calculation fails
            return obj.total_amount


class CreateOrderItemSerializer(serializers.Serializer):
    service_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1)
    description = serializers.CharField(required=False, allow_blank=True)
    special_instructions = serializers.CharField(required=False, allow_blank=True)
    
    def validate_service_id(self, value):
        try:
            Service.objects.get(id=value, is_active=True)
        except Service.DoesNotExist:
            raise serializers.ValidationError("Service not found or inactive.")
        return value
    
    def validate_variant_id(self, value):
        if value:
            try:
                ServiceVariant.objects.get(id=value, is_active=True)
            except ServiceVariant.DoesNotExist:
                raise serializers.ValidationError("Service variant not found or inactive.")
        return value


class CreateOrderSerializer(serializers.ModelSerializer):
    items = CreateOrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = [
            'order_type', 'pickup_address', 'pickup_date', 'pickup_time_slot',
            'delivery_address', 'delivery_date', 'delivery_time_slot',
            'special_instructions', 'items'
        ]
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        return value
    
    def validate_pickup_date(self, value):
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError("Pickup date cannot be in the past.")
        return value
    
    def validate_delivery_date(self, value):
        pickup_date = self.initial_data.get('pickup_date')
        if pickup_date and value:
            from datetime import datetime
            pickup_date = datetime.strptime(pickup_date, '%Y-%m-%d').date()
            if value <= pickup_date:
                raise serializers.ValidationError("Delivery date must be after pickup date.")
        return value
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        
        # Create order
        order = Order.objects.create(customer=user, **validated_data)
        
        # Create order items
        for item_data in items_data:
            service = Service.objects.get(id=item_data['service_id'])
            variant = None
            if item_data.get('variant_id'):
                variant = ServiceVariant.objects.get(id=item_data['variant_id'])
            
            OrderItem.objects.create(
                order=order,
                service=service,
                variant=variant,
                quantity=item_data['quantity'],
                description=item_data.get('description', ''),
                special_instructions=item_data.get('special_instructions', '')
            )
        
        # Create initial status history
        OrderStatusHistory.objects.create(
            order=order,
            status='pending',
            notes='Order created',
            updated_by=user
        )
        
        return order


class UpdateOrderStatusSerializer(serializers.ModelSerializer):
    notes = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Order
        fields = ['status', 'notes']
    
    def validate_status(self, value):
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['picked_up', 'cancelled'],
            'picked_up': ['in_process', 'cancelled'],
            'in_process': ['ready', 'cancelled'],
            'ready': ['out_for_delivery', 'cancelled'],
            'out_for_delivery': ['delivered', 'cancelled'],
            'delivered': [],
            'cancelled': [],
        }
        
        current_status = self.instance.status if self.instance else 'pending'
        allowed_transitions = valid_transitions.get(current_status, [])
        
        if value not in allowed_transitions:
            raise serializers.ValidationError(
                f"Cannot transition from '{current_status}' to '{value}'"
            )
        
        return value
    
    def update(self, instance, validated_data):
        old_status = instance.status
        notes = validated_data.pop('notes', '')
        
        # Update order status
        instance.status = validated_data['status']
        instance.save()
        
        # Create status history entry
        OrderStatusHistory.objects.create(
            order=instance,
            status=instance.status,
            notes=notes,
            updated_by=self.context['request'].user
        )
        
        return instance


class OrderListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    item_count = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer_name', 'status', 'order_type',
            'pickup_date', 'delivery_date', 'total_amount', 'payment_status',
            'item_count', 'created_at'
        ]
        read_only_fields = ['id', 'order_number', 'customer_name', 'created_at']
    
    def get_item_count(self, obj):
        return obj.items.count()
    
    def get_total_amount(self, obj):
        """Calculate total amount dynamically from order items"""
        try:
            # Calculate subtotal from order items
            subtotal = sum(item.total_price for item in obj.items.all())
            
            # Calculate tax (5% GST)
            tax = subtotal * 0.05
            
            # Calculate delivery fee (free for orders above ₹500, else ₹50)
            delivery_fee = 0 if subtotal >= 500 else 50
            
            # Calculate total
            total = subtotal + tax + delivery_fee
            
            return total
        except Exception:
            # Fallback to stored value if calculation fails
            return obj.total_amount


class OrderFilterSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES, required=False)
    order_type = serializers.ChoiceField(choices=Order.ORDER_TYPE_CHOICES, required=False)
    payment_status = serializers.ChoiceField(choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ], required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    min_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False) 