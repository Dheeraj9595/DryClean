from django.db import models
from django.contrib.auth.models import User
from orders.models import Order


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('stripe', 'Stripe'),
        ('razorpay', 'Razorpay'),
        ('paypal', 'PayPal'),
        ('cod', 'Cash on Delivery'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Gateway-specific fields
    gateway_payment_id = models.CharField(max_length=255, blank=True, null=True)
    gateway_order_id = models.CharField(max_length=255, blank=True, null=True)
    gateway_signature = models.TextField(blank=True, null=True)
    
    # Error handling
    error_message = models.TextField(blank=True, null=True)
    error_code = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Payment {self.id} - {self.order.order_number} - {self.status}"
    
    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ['-created_at']


class PaymentTransaction(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, choices=Payment.STATUS_CHOICES)
    
    # Gateway response data
    gateway_response = models.JSONField(blank=True, null=True)
    gateway_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"
    
    class Meta:
        verbose_name = "Payment Transaction"
        verbose_name_plural = "Payment Transactions"
        ordering = ['-created_at']


class Refund(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Gateway-specific fields
    gateway_refund_id = models.CharField(max_length=255, blank=True, null=True)
    gateway_response = models.JSONField(blank=True, null=True)
    
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Refund {self.id} - {self.payment.order.order_number}"
    
    class Meta:
        verbose_name = "Refund"
        verbose_name_plural = "Refunds"
        ordering = ['-created_at']


class PaymentMethod(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    payment_method = models.CharField(max_length=20, choices=Payment.PAYMENT_METHOD_CHOICES)
    
    # For card payments
    card_last4 = models.CharField(max_length=4, blank=True, null=True)
    card_brand = models.CharField(max_length=20, blank=True, null=True)
    card_exp_month = models.PositiveIntegerField(blank=True, null=True)
    card_exp_year = models.PositiveIntegerField(blank=True, null=True)
    
    # Gateway-specific data
    gateway_payment_method_id = models.CharField(max_length=255, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.card_last4:
            return f"{self.card_brand} ****{self.card_last4}"
        return f"{self.payment_method} - {self.user.username}"
    
    class Meta:
        verbose_name = "Payment Method"
        verbose_name_plural = "Payment Methods"
        ordering = ['-is_default', '-created_at']
