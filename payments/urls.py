from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment management
    path('', views.PaymentListView.as_view(), name='payment_list'),
    path('<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('stats/', views.payment_stats, name='payment_stats'),
    
    # Payment methods
    path('payment-methods/', views.PaymentMethodListView.as_view(), name='payment_method_list'),
    path('payment-methods/<int:pk>/', views.PaymentMethodDetailView.as_view(), name='payment_method_detail'),
    
    # Payment gateways
    path('stripe/create-intent/', views.create_stripe_payment_intent, name='stripe_create_intent'),
    path('razorpay/create-order/', views.create_razorpay_order, name='razorpay_create_order'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    
    # Webhooks
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('webhooks/razorpay/', views.razorpay_webhook, name='razorpay_webhook'),
    
    # Refunds
    path('refunds/', views.RefundListView.as_view(), name='refund_list'),
    path('refunds/<int:pk>/', views.RefundDetailView.as_view(), name='refund_detail'),
    path('refunds/<int:refund_id>/process/', views.process_refund, name='process_refund'),
] 