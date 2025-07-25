from django.contrib import admin
from .models import ServiceCategory, Service, ServiceVariant, PricingRule


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'icon')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class ServiceVariantInline(admin.TabularInline):
    model = ServiceVariant
    extra = 1
    fields = ('name', 'price_modifier', 'is_active')


class PricingRuleInline(admin.TabularInline):
    model = PricingRule
    extra = 1
    fields = ('variant', 'min_quantity', 'max_quantity', 'price_per_unit', 'is_active')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'base_price', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ServiceVariantInline, PricingRuleInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'description')
        }),
        ('Pricing', {
            'fields': ('base_price',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ServiceVariant)
class ServiceVariantAdmin(admin.ModelAdmin):
    list_display = ('name', 'service', 'price_modifier', 'final_price', 'is_active')
    list_filter = ('service', 'is_active', 'created_at')
    search_fields = ('name', 'service__name')
    readonly_fields = ('final_price', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('service', 'name')
        }),
        ('Pricing', {
            'fields': ('price_modifier', 'final_price')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    list_display = ('service', 'variant', 'min_quantity', 'max_quantity', 'price_per_unit', 'is_active')
    list_filter = ('service', 'variant', 'is_active', 'created_at')
    search_fields = ('service__name', 'variant__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Service Information', {
            'fields': ('service', 'variant')
        }),
        ('Quantity Range', {
            'fields': ('min_quantity', 'max_quantity')
        }),
        ('Pricing', {
            'fields': ('price_per_unit',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
