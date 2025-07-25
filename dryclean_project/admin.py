from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from accounts.models import UserProfile
from orders.models import Order, OrderItem, OrderStatusHistory, PickupSchedule, DeliverySchedule
from services.models import Service, ServiceCategory, ServiceVariant, PricingRule
from payments.models import Payment, PaymentTransaction, Refund, PaymentMethod
from notifications.models import Notification, EmailTemplate, SMSTemplate, NotificationPreference


# Inline admin classes
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone_number', 'get_address')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    def get_phone_number(self, obj):
        try:
            return obj.userprofile.phone_number
        except UserProfile.DoesNotExist:
            return '-'
    get_phone_number.short_description = 'Phone Number'
    
    def get_address(self, obj):
        try:
            profile = obj.userprofile
            if profile.address:
                return f"{profile.city}, {profile.state}" if profile.city and profile.state else profile.address
            return '-'
        except UserProfile.DoesNotExist:
            return '-'
    get_address.short_description = 'Address'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('unit_price', 'total_price')
    fields = ('service', 'variant', 'quantity', 'unit_price', 'total_price', 'description', 'special_instructions')


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('created_at', 'updated_by_name')
    fields = ('status', 'notes', 'created_at', 'updated_by_name')


class PickupScheduleInline(admin.StackedInline):
    model = PickupSchedule
    extra = 0
    fields = ('scheduled_date', 'scheduled_time_slot', 'actual_pickup_time', 'pickup_agent', 'notes', 'is_completed')


class DeliveryScheduleInline(admin.StackedInline):
    model = DeliverySchedule
    extra = 0
    fields = ('scheduled_date', 'scheduled_time_slot', 'actual_delivery_time', 'delivery_agent', 'notes', 'is_completed')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'status', 'order_type', 'total_amount_display', 'payment_status', 'created_at', 'pickup_date')
    list_filter = ('status', 'order_type', 'payment_status', 'created_at', 'pickup_date')
    search_fields = ('order_number', 'customer__username', 'customer__first_name', 'customer__last_name')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'total_amount_display')
    inlines = [OrderItemInline, OrderStatusHistoryInline, PickupScheduleInline, DeliveryScheduleInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status', 'order_type', 'payment_status', 'payment_method')
        }),
        ('Pickup Information', {
            'fields': ('pickup_address', 'pickup_date', 'pickup_time_slot')
        }),
        ('Delivery Information', {
            'fields': ('delivery_address', 'delivery_date', 'delivery_time_slot')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax', 'delivery_fee', 'total_amount_display')
        }),
        ('Additional Information', {
            'fields': ('special_instructions', 'estimated_completion', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def customer_name(self, obj):
        return f"{obj.customer.get_full_name()} ({obj.customer.username})"
    customer_name.short_description = 'Customer'
    
    def total_amount_display(self, obj):
        return f"₹{obj.total_amount}"
    total_amount_display.short_description = 'Total Amount'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer')


class ServiceVariantInline(admin.TabularInline):
    model = ServiceVariant
    extra = 0
    fields = ('name', 'price_modifier', 'is_active')


class PricingRuleInline(admin.TabularInline):
    model = PricingRule
    extra = 0
    fields = ('min_quantity', 'max_quantity', 'price_per_unit')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'base_price', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    inlines = [ServiceVariantInline, PricingRuleInline]
    
    fieldsets = (
        ('Service Information', {
            'fields': ('name', 'description', 'category', 'base_price', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'service_count')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    
    def service_count(self, obj):
        return obj.services.count()
    service_count.short_description = 'Services'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_number', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order__order_number', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')
    
    def order_number(self, obj):
        return obj.order.order_number if obj.order else '-'
    order_number.short_description = 'Order Number'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'type', 'title', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')
    readonly_fields = ('created_at')


# Register models
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(OrderItem)
admin.site.register(OrderStatusHistory)
admin.site.register(PickupSchedule)
admin.site.register(DeliverySchedule)

admin.site.register(ServiceVariant)
admin.site.register(PricingRule)

admin.site.register(PaymentTransaction)
admin.site.register(Refund)
admin.site.register(PaymentMethod)

admin.site.register(EmailTemplate)
admin.site.register(SMSTemplate)
admin.site.register(NotificationPreference)

# Customize admin site
admin.site.site_header = "DryClean Administration"
admin.site.site_title = "DryClean Admin Portal"
admin.site.index_title = "Welcome to DryClean Administration" 