from django.db import models
from django.contrib.auth.models import User
from services.models import Service, ServiceVariant
from decimal import Decimal


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('picked_up', 'Picked Up'),
        ('in_process', 'In Process'),
        ('ready', 'Ready for Delivery'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    ORDER_TYPE_CHOICES = [
        ('pickup', 'Pickup'),
        ('dropoff', 'Drop Off'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES, default='pickup')
    
    # Pickup and Delivery Information
    pickup_address = models.TextField()
    pickup_date = models.DateField()
    pickup_time_slot = models.CharField(max_length=50)  # e.g., "9:00 AM - 12:00 PM"
    delivery_address = models.TextField(blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)
    delivery_time_slot = models.CharField(max_length=50, blank=True, null=True)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Payment
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ], default='pending')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    
    # Additional Information
    special_instructions = models.TextField(blank=True, null=True)
    estimated_completion = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.order_number} - {self.customer.username}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number
            last_order = Order.objects.order_by('-id').first()
            if last_order:
                last_number = int(last_order.order_number[3:])  # Remove "ORD" prefix
                self.order_number = f"ORD{last_number + 1:06d}"
            else:
                self.order_number = "ORD000001"
        
        # Calculate totals
        self.calculate_totals()
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate order totals based on items"""
        try:
            subtotal = sum(item.total_price for item in self.items.all())
        except ValueError:
            # Handle case when order doesn't have a primary key yet
            subtotal = Decimal('0.00')
        
        self.subtotal = subtotal
        
        # Calculate tax (assuming 5% GST)
        self.tax = subtotal * Decimal('0.05')
        
        # Calculate delivery fee (free for orders above ₹500, else ₹50)
        if subtotal >= 500:
            self.delivery_fee = Decimal('0.00')
        else:
            self.delivery_fee = Decimal('50.00')
        
        self.total_amount = self.subtotal + self.tax + self.delivery_fee
    
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    variant = models.ForeignKey(ServiceVariant, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Item-specific details
    description = models.CharField(max_length=255, blank=True, null=True)
    special_instructions = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        variant_text = f" - {self.variant.name}" if self.variant else ""
        return f"{self.service.name}{variant_text} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        if not self.unit_price:
            if self.variant:
                self.unit_price = self.variant.final_price
            else:
                self.unit_price = self.service.base_price
        
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    notes = models.TextField(blank=True, null=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.order.order_number} - {self.status}"
    
    class Meta:
        verbose_name = "Order Status History"
        verbose_name_plural = "Order Status History"
        ordering = ['-created_at']


class PickupSchedule(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='pickup_schedule')
    scheduled_date = models.DateField()
    scheduled_time_slot = models.CharField(max_length=50)
    actual_pickup_time = models.DateTimeField(blank=True, null=True)
    pickup_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pickup_assignments')
    notes = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Pickup for {self.order.order_number}"
    
    class Meta:
        verbose_name = "Pickup Schedule"
        verbose_name_plural = "Pickup Schedules"


class DeliverySchedule(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery_schedule')
    scheduled_date = models.DateField()
    scheduled_time_slot = models.CharField(max_length=50)
    actual_delivery_time = models.DateTimeField(blank=True, null=True)
    delivery_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='delivery_assignments')
    notes = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Delivery for {self.order.order_number}"
    
    class Meta:
        verbose_name = "Delivery Schedule"
        verbose_name_plural = "Delivery Schedules"
