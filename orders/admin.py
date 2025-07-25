from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory, PickupSchedule, DeliverySchedule


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('unit_price', 'total_price')
    fields = ('service', 'variant', 'quantity', 'unit_price', 'total_price', 'description', 'special_instructions')


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('status', 'notes', 'updated_by', 'created_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'status', 'order_type', 'total_amount', 'payment_status', 'created_at')
    list_filter = ('status', 'order_type', 'payment_status', 'created_at', 'pickup_date')
    search_fields = ('order_number', 'customer__username', 'customer__email', 'pickup_address')
    readonly_fields = ('order_number', 'subtotal', 'tax', 'delivery_fee', 'total_amount', 'created_at', 'updated_at')
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status', 'order_type')
        }),
        ('Pickup Information', {
            'fields': ('pickup_address', 'pickup_date', 'pickup_time_slot')
        }),
        ('Delivery Information', {
            'fields': ('delivery_address', 'delivery_date', 'delivery_time_slot')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax', 'delivery_fee', 'total_amount')
        }),
        ('Payment', {
            'fields': ('payment_status', 'payment_method')
        }),
        ('Additional Information', {
            'fields': ('special_instructions', 'estimated_completion')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_picked_up', 'mark_as_in_process', 'mark_as_ready', 'mark_as_delivered']
    
    def mark_as_confirmed(self, request, queryset):
        for order in queryset:
            if order.status == 'pending':
                order.status = 'confirmed'
                order.save()
                OrderStatusHistory.objects.create(
                    order=order,
                    status='confirmed',
                    notes='Order confirmed by admin',
                    updated_by=request.user
                )
        self.message_user(request, f"{queryset.count()} orders marked as confirmed.")
    mark_as_confirmed.short_description = "Mark selected orders as confirmed"
    
    def mark_as_picked_up(self, request, queryset):
        for order in queryset:
            if order.status == 'confirmed':
                order.status = 'picked_up'
                order.save()
                OrderStatusHistory.objects.create(
                    order=order,
                    status='picked_up',
                    notes='Order picked up',
                    updated_by=request.user
                )
        self.message_user(request, f"{queryset.count()} orders marked as picked up.")
    mark_as_picked_up.short_description = "Mark selected orders as picked up"
    
    def mark_as_in_process(self, request, queryset):
        for order in queryset:
            if order.status == 'picked_up':
                order.status = 'in_process'
                order.save()
                OrderStatusHistory.objects.create(
                    order=order,
                    status='in_process',
                    notes='Order in processing',
                    updated_by=request.user
                )
        self.message_user(request, f"{queryset.count()} orders marked as in process.")
    mark_as_in_process.short_description = "Mark selected orders as in process"
    
    def mark_as_ready(self, request, queryset):
        for order in queryset:
            if order.status == 'in_process':
                order.status = 'ready'
                order.save()
                OrderStatusHistory.objects.create(
                    order=order,
                    status='ready',
                    notes='Order ready for delivery',
                    updated_by=request.user
                )
        self.message_user(request, f"{queryset.count()} orders marked as ready.")
    mark_as_ready.short_description = "Mark selected orders as ready"
    
    def mark_as_delivered(self, request, queryset):
        for order in queryset:
            if order.status == 'ready':
                order.status = 'delivered'
                order.save()
                OrderStatusHistory.objects.create(
                    order=order,
                    status='delivered',
                    notes='Order delivered',
                    updated_by=request.user
                )
        self.message_user(request, f"{queryset.count()} orders marked as delivered.")
    mark_as_delivered.short_description = "Mark selected orders as delivered"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'service', 'variant', 'quantity', 'unit_price', 'total_price')
    list_filter = ('service', 'variant', 'created_at')
    search_fields = ('order__order_number', 'service__name', 'variant__name')
    readonly_fields = ('unit_price', 'total_price', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order',)
        }),
        ('Item Information', {
            'fields': ('service', 'variant', 'quantity')
        }),
        ('Pricing', {
            'fields': ('unit_price', 'total_price')
        }),
        ('Additional Information', {
            'fields': ('description', 'special_instructions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'updated_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number', 'updated_by__username', 'notes')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order', 'status')
        }),
        ('Update Information', {
            'fields': ('notes', 'updated_by')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(PickupSchedule)
class PickupScheduleAdmin(admin.ModelAdmin):
    list_display = ('order', 'scheduled_date', 'scheduled_time_slot', 'pickup_agent', 'is_completed')
    list_filter = ('scheduled_date', 'is_completed', 'created_at')
    search_fields = ('order__order_number', 'pickup_agent__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order',)
        }),
        ('Schedule Information', {
            'fields': ('scheduled_date', 'scheduled_time_slot')
        }),
        ('Agent Information', {
            'fields': ('pickup_agent',)
        }),
        ('Completion', {
            'fields': ('actual_pickup_time', 'is_completed', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DeliverySchedule)
class DeliveryScheduleAdmin(admin.ModelAdmin):
    list_display = ('order', 'scheduled_date', 'scheduled_time_slot', 'delivery_agent', 'is_completed')
    list_filter = ('scheduled_date', 'is_completed', 'created_at')
    search_fields = ('order__order_number', 'delivery_agent__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order',)
        }),
        ('Schedule Information', {
            'fields': ('scheduled_date', 'scheduled_time_slot')
        }),
        ('Agent Information', {
            'fields': ('delivery_agent',)
        }),
        ('Completion', {
            'fields': ('actual_delivery_time', 'is_completed', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
