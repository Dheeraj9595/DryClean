from rest_framework import serializers
from .models import ServiceCategory, Service, ServiceVariant, PricingRule


class ServiceVariantSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceVariant
        fields = [
            'id', 'name', 'price_modifier', 'final_price', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_final_price(self, obj):
        try:
            return float(obj.final_price)
        except (AttributeError, TypeError, ValueError):
            return float(obj.service.base_price) + float(obj.price_modifier or 0)


class ServiceSerializer(serializers.ModelSerializer):
    variants = ServiceVariantSerializer(many=True, read_only=True)
    
    class Meta:
        model = Service
        fields = [
            'id', 'category', 'name', 'description', 'base_price', 
            'is_active', 'variants', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServiceCategorySerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = ServiceCategory
        fields = [
            'id', 'name', 'description', 'icon', 'is_active', 
            'services', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PricingRuleSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True)
    
    class Meta:
        model = PricingRule
        fields = [
            'id', 'service', 'service_name', 'variant', 'variant_name',
            'min_quantity', 'max_quantity', 'price_per_unit', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServiceWithPricingSerializer(serializers.ModelSerializer):
    variants = ServiceVariantSerializer(many=True, read_only=True)
    pricing_rules = PricingRuleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Service
        fields = [
            'id', 'category', 'name', 'description', 'base_price', 
            'is_active', 'variants', 'pricing_rules', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServiceEstimateSerializer(serializers.Serializer):
    service_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1)
    
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


class BulkEstimateSerializer(serializers.Serializer):
    items = ServiceEstimateSerializer(many=True)
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        return value 