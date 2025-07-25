from django.shortcuts import render
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone
import stripe
import razorpay
from .models import Payment, PaymentTransaction, Refund, PaymentMethod
from .serializers import (
    PaymentSerializer, CreatePaymentSerializer, PaymentMethodSerializer,
    PaymentMethodCreateSerializer, PaymentMethodUpdateSerializer,
    RefundSerializer, CreateRefundSerializer
)
from orders.models import Order
from django.db.models import Sum

# Initialize payment gateways
stripe.api_key = settings.STRIPE_SECRET_KEY
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


class PaymentListView(generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreatePaymentSerializer
        return PaymentSerializer


class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)


class PaymentMethodListView(generics.ListCreateAPIView):
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user, is_active=True)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PaymentMethodCreateSerializer
        return PaymentMethodSerializer


class PaymentMethodDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PaymentMethodUpdateSerializer
        return PaymentMethodSerializer


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_stripe_payment_intent(request):
    """Create Stripe payment intent"""
    serializer = CreatePaymentSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        payment = serializer.save()
        
        try:
            # Create Stripe payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(payment.amount * 100),  # Convert to cents
                currency=payment.currency.lower(),
                metadata={
                    'payment_id': payment.id,
                    'order_id': payment.order.id,
                    'user_id': payment.user.id,
                }
            )
            
            # Update payment with gateway order ID
            payment.gateway_order_id = intent.id
            payment.save()
            
            return Response({
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'payment_id': payment.id,
            })
            
        except stripe.error.StripeError as e:
            payment.status = 'failed'
            payment.error_message = str(e)
            payment.save()
            
            return Response({
                'error': 'Payment failed.',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_razorpay_order(request):
    """Create Razorpay order"""
    serializer = CreatePaymentSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        payment = serializer.save()
        
        try:
            # Create Razorpay order
            order_data = {
                'amount': int(payment.amount * 100),  # Convert to paise
                'currency': payment.currency,
                'receipt': f'order_{payment.order.order_number}',
                'notes': {
                    'payment_id': str(payment.id),
                    'order_id': str(payment.order.id),
                    'user_id': str(payment.user.id),
                }
            }
            
            razorpay_order = razorpay_client.order.create(data=order_data)
            
            # Update payment with gateway order ID
            payment.gateway_order_id = razorpay_order['id']
            payment.save()
            
            return Response({
                'order_id': razorpay_order['id'],
                'amount': razorpay_order['amount'],
                'currency': razorpay_order['currency'],
                'payment_id': payment.id,
            })
            
        except Exception as e:
            payment.status = 'failed'
            payment.error_message = str(e)
            payment.save()
            
            return Response({
                'error': 'Payment failed.',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError as e:
        return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_stripe_payment_success(payment_intent)
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_stripe_payment_failure(payment_intent)
    
    return Response({'status': 'success'})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def razorpay_webhook(request):
    """Handle Razorpay webhooks"""
    # Verify webhook signature
    webhook_signature = request.META.get('HTTP_X_RAZORPAY_SIGNATURE')
    
    try:
        razorpay_client.utility.verify_webhook_signature(
            request.body.decode(),
            webhook_signature,
            settings.RAZORPAY_WEBHOOK_SECRET
        )
    except Exception as e:
        return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Parse webhook data
    webhook_data = request.data
    
    if webhook_data.get('event') == 'payment.captured':
        handle_razorpay_payment_success(webhook_data['payload']['payment']['entity'])
    elif webhook_data.get('event') == 'payment.failed':
        handle_razorpay_payment_failure(webhook_data['payload']['payment']['entity'])
    
    return Response({'status': 'success'})


def handle_stripe_payment_success(payment_intent):
    """Handle successful Stripe payment"""
    try:
        payment = Payment.objects.get(gateway_order_id=payment_intent['id'])
        payment.status = 'completed'
        payment.gateway_payment_id = payment_intent['id']
        payment.completed_at = timezone.now()
        payment.save()
        
        # Update order payment status
        order = payment.order
        order.payment_status = 'paid'
        order.payment_method = 'stripe'
        order.save()
        
        # Create payment transaction
        PaymentTransaction.objects.create(
            payment=payment,
            transaction_id=payment_intent['id'],
            amount=payment.amount,
            currency=payment.currency,
            status='completed',
            gateway_response=payment_intent,
        )
        
    except Payment.DoesNotExist:
        pass


def handle_stripe_payment_failure(payment_intent):
    """Handle failed Stripe payment"""
    try:
        payment = Payment.objects.get(gateway_order_id=payment_intent['id'])
        payment.status = 'failed'
        payment.error_message = payment_intent.get('last_payment_error', {}).get('message', 'Payment failed')
        payment.save()
        
        # Create payment transaction
        PaymentTransaction.objects.create(
            payment=payment,
            transaction_id=payment_intent['id'],
            amount=payment.amount,
            currency=payment.currency,
            status='failed',
            gateway_response=payment_intent,
        )
        
    except Payment.DoesNotExist:
        pass


def handle_razorpay_payment_success(payment_data):
    """Handle successful Razorpay payment"""
    try:
        payment = Payment.objects.get(gateway_order_id=payment_data['order_id'])
        payment.status = 'completed'
        payment.gateway_payment_id = payment_data['id']
        payment.completed_at = timezone.now()
        payment.save()
        
        # Update order payment status
        order = payment.order
        order.payment_status = 'paid'
        order.payment_method = 'razorpay'
        order.save()
        
        # Create payment transaction
        PaymentTransaction.objects.create(
            payment=payment,
            transaction_id=payment_data['id'],
            amount=payment.amount,
            currency=payment.currency,
            status='completed',
            gateway_response=payment_data,
        )
        
    except Payment.DoesNotExist:
        pass


def handle_razorpay_payment_failure(payment_data):
    """Handle failed Razorpay payment"""
    try:
        payment = Payment.objects.get(gateway_order_id=payment_data['order_id'])
        payment.status = 'failed'
        payment.error_message = payment_data.get('error_description', 'Payment failed')
        payment.save()
        
        # Create payment transaction
        PaymentTransaction.objects.create(
            payment=payment,
            transaction_id=payment_data['id'],
            amount=payment.amount,
            currency=payment.currency,
            status='failed',
            gateway_response=payment_data,
        )
        
    except Payment.DoesNotExist:
        pass


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_payment(request):
    """Verify payment completion"""
    payment_id = request.data.get('payment_id')
    payment_method = request.data.get('payment_method')
    
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user)
        
        if payment_method == 'stripe':
            # Verify with Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment.gateway_order_id)
            if payment_intent.status == 'succeeded':
                handle_stripe_payment_success(payment_intent)
                return Response({'status': 'success'})
        
        elif payment_method == 'razorpay':
            # Verify with Razorpay
            payment_data = razorpay_client.payment.fetch(payment.gateway_payment_id)
            if payment_data['status'] == 'captured':
                handle_razorpay_payment_success(payment_data)
                return Response({'status': 'success'})
        
        return Response({'status': 'pending'})
        
    except Payment.DoesNotExist:
        return Response({
            'error': 'Payment not found.'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': 'Verification failed.',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


class RefundListView(generics.ListCreateAPIView):
    serializer_class = RefundSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Refund.objects.all()
        return Refund.objects.filter(payment__user=user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateRefundSerializer
        return RefundSerializer


class RefundDetailView(generics.RetrieveAPIView):
    serializer_class = RefundSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Refund.objects.all()
        return Refund.objects.filter(payment__user=user)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def process_refund(request, refund_id):
    """Process refund through payment gateway"""
    try:
        refund = Refund.objects.get(id=refund_id)
        
        if refund.payment.payment_method == 'stripe':
            # Process Stripe refund
            stripe_refund = stripe.Refund.create(
                payment_intent=refund.payment.gateway_payment_id,
                amount=int(refund.amount * 100),
                reason='requested_by_customer'
            )
            
            refund.gateway_refund_id = stripe_refund.id
            refund.status = 'completed'
            refund.completed_at = timezone.now()
            refund.gateway_response = stripe_refund
            refund.save()
            
        elif refund.payment.payment_method == 'razorpay':
            # Process Razorpay refund
            razorpay_refund = razorpay_client.payment.refund(
                refund.payment.gateway_payment_id,
                {
                    'amount': int(refund.amount * 100),
                    'speed': 'normal'
                }
            )
            
            refund.gateway_refund_id = razorpay_refund['id']
            refund.status = 'completed'
            refund.completed_at = timezone.now()
            refund.gateway_response = razorpay_refund
            refund.save()
        
        return Response({
            'message': 'Refund processed successfully.'
        })
        
    except Refund.DoesNotExist:
        return Response({
            'error': 'Refund not found.'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': 'Refund processing failed.',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_stats(request):
    """Get payment statistics for user"""
    user = request.user
    
    payments = Payment.objects.filter(user=user)
    
    stats = {
        'total_payments': payments.count(),
        'total_amount': payments.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0,
        'pending_payments': payments.filter(status='pending').count(),
        'failed_payments': payments.filter(status='failed').count(),
        'completed_payments': payments.filter(status='completed').count(),
    }
    
    return Response(stats)
