from django.contrib import admin
from .models import Payment, PaymentTransaction, Refund, PaymentMethod
from django.utils import timezone


class PaymentTransactionInline(admin.TabularInline):
    model = PaymentTransaction
    extra = 0
    readonly_fields = ('transaction_id', 'gateway_response', 'created_at')
    fields = ('transaction_id', 'amount', 'currency', 'status', 'gateway_fee', 'gateway_response')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'user', 'payment_method', 'amount', 'status', 'created_at')
    list_filter = ('payment_method', 'status', 'currency', 'created_at')
    search_fields = ('order__order_number', 'user__username', 'user__email', 'gateway_payment_id')
    readonly_fields = ('gateway_payment_id', 'gateway_order_id', 'gateway_signature', 'error_message', 'error_code', 'created_at', 'updated_at', 'completed_at')
    inlines = [PaymentTransactionInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order', 'user')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'amount', 'currency', 'status')
        }),
        ('Gateway Information', {
            'fields': ('gateway_payment_id', 'gateway_order_id', 'gateway_signature'),
            'classes': ('collapse',)
        }),
        ('Error Information', {
            'fields': ('error_message', 'error_code'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_failed']
    
    def mark_as_completed(self, request, queryset):
        for payment in queryset:
            if payment.status == 'pending':
                payment.status = 'completed'
                payment.completed_at = timezone.now()
                payment.save()
                
                # Update order payment status
                payment.order.payment_status = 'paid'
                payment.order.payment_method = payment.payment_method
                payment.order.save()
        self.message_user(request, f"{queryset.count()} payments marked as completed.")
    mark_as_completed.short_description = "Mark selected payments as completed"
    
    def mark_as_failed(self, request, queryset):
        for payment in queryset:
            if payment.status == 'pending':
                payment.status = 'failed'
                payment.save()
        self.message_user(request, f"{queryset.count()} payments marked as failed.")
    mark_as_failed.short_description = "Mark selected payments as failed"


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'payment', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('transaction_id', 'payment__order__order_number')
    readonly_fields = ('gateway_response', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('payment', 'transaction_id', 'amount', 'currency', 'status')
        }),
        ('Gateway Information', {
            'fields': ('gateway_response', 'gateway_fee')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'amount', 'status', 'processed_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('payment__order__order_number', 'processed_by__username', 'gateway_refund_id')
    readonly_fields = ('gateway_refund_id', 'gateway_response', 'created_at', 'updated_at', 'completed_at')
    
    fieldsets = (
        ('Refund Information', {
            'fields': ('payment', 'amount', 'reason', 'status')
        }),
        ('Processing Information', {
            'fields': ('processed_by',)
        }),
        ('Gateway Information', {
            'fields': ('gateway_refund_id', 'gateway_response'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_failed']
    
    def mark_as_completed(self, request, queryset):
        for refund in queryset:
            if refund.status == 'pending':
                refund.status = 'completed'
                refund.completed_at = timezone.now()
                refund.save()
        self.message_user(request, f"{queryset.count()} refunds marked as completed.")
    mark_as_completed.short_description = "Mark selected refunds as completed"
    
    def mark_as_failed(self, request, queryset):
        for refund in queryset:
            if refund.status == 'pending':
                refund.status = 'failed'
                refund.save()
        self.message_user(request, f"{queryset.count()} refunds marked as failed.")
    mark_as_failed.short_description = "Mark selected refunds as failed"


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_method', 'card_brand', 'card_last4', 'is_default', 'is_active')
    list_filter = ('payment_method', 'card_brand', 'is_default', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'card_last4')
    readonly_fields = ('gateway_payment_method_id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Payment Method Information', {
            'fields': ('payment_method', 'is_default', 'is_active')
        }),
        ('Card Information', {
            'fields': ('card_last4', 'card_brand', 'card_exp_month', 'card_exp_year'),
            'classes': ('collapse',)
        }),
        ('Gateway Information', {
            'fields': ('gateway_payment_method_id',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
