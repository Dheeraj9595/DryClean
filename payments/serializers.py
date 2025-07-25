from rest_framework import serializers
from .models import Payment, PaymentTransaction, Refund, PaymentMethod
from orders.models import Order
from django.db import models


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'payment_method', 'card_last4', 'card_brand', 'card_exp_month',
            'card_exp_year', 'is_default', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'payment', 'transaction_id', 'amount', 'currency', 'status',
            'gateway_response', 'gateway_fee', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentSerializer(serializers.ModelSerializer):
    transactions = PaymentTransactionSerializer(many=True, read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    customer_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'order_number', 'user', 'customer_name', 'payment_method',
            'amount', 'currency', 'status', 'gateway_payment_id', 'gateway_order_id',
            'gateway_signature', 'error_message', 'error_code', 'transactions',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'customer_name', 'gateway_payment_id',
            'gateway_order_id', 'gateway_signature', 'error_message', 'error_code',
            'transactions', 'created_at', 'updated_at', 'completed_at'
        ]


class CreatePaymentSerializer(serializers.ModelSerializer):
    payment_method_id = serializers.IntegerField(required=False)
    
    class Meta:
        model = Payment
        fields = ['order', 'payment_method', 'payment_method_id', 'amount', 'currency']
    
    def validate_order(self, value):
        user = self.context['request'].user
        if value.customer != user:
            raise serializers.ValidationError("You can only create payments for your own orders.")
        
        if value.payment_status == 'paid':
            raise serializers.ValidationError("Order is already paid.")
        
        return value
    
    def validate_amount(self, value):
        order = self.initial_data.get('order')
        if order:
            try:
                order_obj = Order.objects.get(id=order)
                if value != order_obj.total_amount:
                    raise serializers.ValidationError("Payment amount must match order total.")
            except Order.DoesNotExist:
                raise serializers.ValidationError("Order not found.")
        
        return value
    
    def create(self, validated_data):
        payment_method_id = validated_data.pop('payment_method_id', None)
        user = self.context['request'].user
        
        payment = Payment.objects.create(user=user, **validated_data)
        
        # If payment method ID is provided, get the payment method
        if payment_method_id:
            try:
                payment_method = PaymentMethod.objects.get(
                    id=payment_method_id,
                    user=user,
                    is_active=True
                )
                # You can store additional payment method info here if needed
            except PaymentMethod.DoesNotExist:
                pass
        
        return payment


class StripePaymentIntentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    payment_method_id = serializers.CharField(required=False)
    
    def validate_order_id(self, value):
        try:
            order = Order.objects.get(id=value)
            user = self.context['request'].user
            if order.customer != user:
                raise serializers.ValidationError("You can only create payments for your own orders.")
            
            if order.payment_status == 'paid':
                raise serializers.ValidationError("Order is already paid.")
            
            return order
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")


class RazorpayOrderSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    
    def validate_order_id(self, value):
        try:
            order = Order.objects.get(id=value)
            user = self.context['request'].user
            if order.customer != user:
                raise serializers.ValidationError("You can only create payments for your own orders.")
            
            if order.payment_status == 'paid':
                raise serializers.ValidationError("Order is already paid.")
            
            return order
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")


class PaymentVerificationSerializer(serializers.Serializer):
    payment_id = serializers.CharField()
    order_id = serializers.CharField()
    signature = serializers.CharField(required=False)  # For Razorpay
    payment_intent = serializers.CharField(required=False)  # For Stripe
    
    def validate(self, attrs):
        payment_method = self.context.get('payment_method')
        
        if payment_method == 'razorpay' and not attrs.get('signature'):
            raise serializers.ValidationError("Signature is required for Razorpay verification.")
        
        if payment_method == 'stripe' and not attrs.get('payment_intent'):
            raise serializers.ValidationError("Payment intent is required for Stripe verification.")
        
        return attrs


class RefundSerializer(serializers.ModelSerializer):
    payment_order_number = serializers.CharField(source='payment.order.order_number', read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)
    
    class Meta:
        model = Refund
        fields = [
            'id', 'payment', 'payment_order_number', 'amount', 'reason', 'status',
            'gateway_refund_id', 'gateway_response', 'processed_by', 'processed_by_name',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'payment_order_number', 'gateway_refund_id', 'gateway_response',
            'processed_by_name', 'created_at', 'updated_at', 'completed_at'
        ]


class CreateRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ['payment', 'amount', 'reason']
    
    def validate_payment(self, value):
        if value.status != 'completed':
            raise serializers.ValidationError("Can only refund completed payments.")
        
        # Check if payment has already been refunded
        if value.refunds.filter(status='completed').exists():
            raise serializers.ValidationError("Payment has already been refunded.")
        
        return value
    
    def validate_amount(self, value):
        payment = self.initial_data.get('payment')
        if payment:
            try:
                payment_obj = Payment.objects.get(id=payment)
                if value > payment_obj.amount:
                    raise serializers.ValidationError("Refund amount cannot exceed payment amount.")
                
                # Check if refund amount exceeds remaining refundable amount
                total_refunded = payment_obj.refunds.filter(status='completed').aggregate(
                    total=models.Sum('amount')
                )['total'] or 0
                
                if value > (payment_obj.amount - total_refunded):
                    raise serializers.ValidationError("Refund amount exceeds remaining refundable amount.")
                
            except Payment.DoesNotExist:
                raise serializers.ValidationError("Payment not found.")
        
        return value
    
    def create(self, validated_data):
        validated_data['processed_by'] = self.context['request'].user
        return super().create(validated_data)


class PaymentMethodCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = [
            'payment_method', 'card_last4', 'card_brand', 'card_exp_month',
            'card_exp_year', 'gateway_payment_method_id'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        
        # If this is the first payment method, make it default
        if not PaymentMethod.objects.filter(user=validated_data['user']).exists():
            validated_data['is_default'] = True
        
        return super().create(validated_data)


class PaymentMethodUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['is_default', 'is_active']
    
    def update(self, instance, validated_data):
        # If making this payment method default, unset others
        if validated_data.get('is_default', False):
            PaymentMethod.objects.filter(
                user=instance.user,
                is_default=True
            ).update(is_default=False)
        
        return super().update(instance, validated_data) 