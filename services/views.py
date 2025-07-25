from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from .models import ServiceCategory, Service, ServiceVariant, PricingRule
from .serializers import (
    ServiceCategorySerializer, ServiceSerializer, ServiceVariantSerializer,
    PricingRuleSerializer, ServiceWithPricingSerializer, ServiceEstimateSerializer,
    BulkEstimateSerializer
)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def debug_services(request):
    """Debug view to test services API"""
    services = Service.objects.filter(is_active=True)[:5]
    data = []
    for service in services:
        data.append({
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'base_price': str(service.base_price),
            'category': service.category.name
        })
    return Response(data)


class ServiceCategoryListView(generics.ListAPIView):
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer
    permission_classes = [permissions.AllowAny]


class ServiceCategoryDetailView(generics.RetrieveAPIView):
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer
    permission_classes = [permissions.AllowAny]


class ServiceListView(generics.ListAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        try:
            queryset = Service.objects.filter(is_active=True)
            category_id = self.request.query_params.get('category', None)
            search = self.request.query_params.get('search', None)
            
            if category_id:
                queryset = queryset.filter(category_id=category_id)
            
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) | 
                    Q(description__icontains=search) |
                    Q(category__name__icontains=search)
                )
            
            return queryset
        except Exception as e:
            # Return empty queryset if there's an error
            return Service.objects.none()
    
    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': f'Failed to load services: {str(e)}'}, status=500)


class ServiceDetailView(generics.RetrieveAPIView):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceWithPricingSerializer
    permission_classes = [permissions.AllowAny]


class ServiceVariantListView(generics.ListAPIView):
    serializer_class = ServiceVariantSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        service_id = self.kwargs.get('service_id')
        return ServiceVariant.objects.filter(
            service_id=service_id,
            service__is_active=True,
            is_active=True
        )


class PricingRuleListView(generics.ListAPIView):
    serializer_class = PricingRuleSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        service_id = self.kwargs.get('service_id')
        return PricingRule.objects.filter(
            service_id=service_id,
            service__is_active=True,
            is_active=True
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def estimate_service(request):
    """Estimate price for a single service"""
    serializer = ServiceEstimateSerializer(data=request.data)
    if serializer.is_valid():
        service_id = serializer.validated_data['service_id']
        variant_id = serializer.validated_data.get('variant_id')
        quantity = serializer.validated_data['quantity']
        
        try:
            service = Service.objects.get(id=service_id, is_active=True)
            unit_price = service.base_price
            
            if variant_id:
                variant = ServiceVariant.objects.get(
                    id=variant_id,
                    service=service,
                    is_active=True
                )
                unit_price = variant.final_price
            
            total_price = unit_price * quantity
            
            # Check for bulk pricing rules
            pricing_rule = PricingRule.objects.filter(
                service=service,
                variant_id=variant_id,
                min_quantity__lte=quantity,
                max_quantity__gte=quantity,
                is_active=True
            ).first()
            
            if pricing_rule:
                total_price = pricing_rule.price_per_unit * quantity
            
            return Response({
                'service_id': service_id,
                'variant_id': variant_id,
                'quantity': quantity,
                'unit_price': unit_price,
                'total_price': total_price,
                'service_name': service.name,
                'variant_name': variant.name if variant_id else None,
            })
            
        except (Service.DoesNotExist, ServiceVariant.DoesNotExist):
            return Response({
                'error': 'Service or variant not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def estimate_bulk_services(request):
    """Estimate price for multiple services"""
    serializer = BulkEstimateSerializer(data=request.data)
    if serializer.is_valid():
        items = serializer.validated_data['items']
        estimates = []
        total_amount = 0
        
        for item in items:
            service_id = item['service_id']
            variant_id = item.get('variant_id')
            quantity = item['quantity']
            
            try:
                service = Service.objects.get(id=service_id, is_active=True)
                unit_price = service.base_price
                
                if variant_id:
                    variant = ServiceVariant.objects.get(
                        id=variant_id,
                        service=service,
                        is_active=True
                    )
                    unit_price = variant.final_price
                
                item_total = unit_price * quantity
                
                # Check for bulk pricing rules
                pricing_rule = PricingRule.objects.filter(
                    service=service,
                    variant_id=variant_id,
                    min_quantity__lte=quantity,
                    max_quantity__gte=quantity,
                    is_active=True
                ).first()
                
                if pricing_rule:
                    item_total = pricing_rule.price_per_unit * quantity
                
                estimates.append({
                    'service_id': service_id,
                    'variant_id': variant_id,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_price': item_total,
                    'service_name': service.name,
                    'variant_name': variant.name if variant_id else None,
                })
                
                total_amount += item_total
                
            except (Service.DoesNotExist, ServiceVariant.DoesNotExist):
                return Response({
                    'error': f'Service or variant not found for item: {item}'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'items': estimates,
            'subtotal': total_amount,
            'tax': total_amount * 0.05,  # 5% GST
            'delivery_fee': 0 if total_amount >= 500 else 50,
            'total_amount': total_amount * 1.05 + (0 if total_amount >= 500 else 50)
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def service_search(request):
    """Search services by name or description"""
    query = request.query_params.get('q', '')
    if not query:
        return Response({
            'error': 'Search query is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    services = Service.objects.filter(
        Q(name__icontains=query) | 
        Q(description__icontains=query) |
        Q(category__name__icontains=query),
        is_active=True
    )[:10]
    
    serializer = ServiceSerializer(services, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def popular_services(request):
    """Get popular services (can be based on order count in the future)"""
    services = Service.objects.filter(is_active=True).order_by('-created_at')[:6]
    serializer = ServiceSerializer(services, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def service_categories_with_services(request):
    """Get all categories with their services"""
    categories = ServiceCategory.objects.filter(is_active=True)
    serializer = ServiceCategorySerializer(categories, many=True)
    return Response(serializer.data)


# Admin views for managing services
class AdminServiceCategoryView(generics.ListCreateAPIView):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [permissions.IsAdminUser]


class AdminServiceCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [permissions.IsAdminUser]


class AdminServiceView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminServiceVariantView(generics.ListCreateAPIView):
    serializer_class = ServiceVariantSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        service_id = self.kwargs.get('service_id')
        return ServiceVariant.objects.filter(service_id=service_id)


class AdminServiceVariantDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceVariant.objects.all()
    serializer_class = ServiceVariantSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminPricingRuleView(generics.ListCreateAPIView):
    serializer_class = PricingRuleSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        service_id = self.kwargs.get('service_id')
        return PricingRule.objects.filter(service_id=service_id)


class AdminPricingRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PricingRule.objects.all()
    serializer_class = PricingRuleSerializer
    permission_classes = [permissions.IsAdminUser]
