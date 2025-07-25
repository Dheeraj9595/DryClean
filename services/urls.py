from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # Debug endpoint
    path('debug/', views.debug_services, name='debug_services'),
    
    # Public endpoints
    path('categories/', views.ServiceCategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/', views.ServiceCategoryDetailView.as_view(), name='category_detail'),
    path('', views.ServiceListView.as_view(), name='service_list'),
    path('<int:pk>/', views.ServiceDetailView.as_view(), name='service_detail'),
    path('<int:service_id>/variants/', views.ServiceVariantListView.as_view(), name='variant_list'),
    path('<int:service_id>/pricing/', views.PricingRuleListView.as_view(), name='pricing_list'),
    
    # Estimation endpoints
    path('estimate/', views.estimate_service, name='estimate_service'),
    path('estimate/bulk/', views.estimate_bulk_services, name='estimate_bulk_services'),
    
    # Search and popular services
    path('search/', views.service_search, name='service_search'),
    path('popular/', views.popular_services, name='popular_services'),
    path('categories-with-services/', views.service_categories_with_services, name='categories_with_services'),
    
    # Admin endpoints
    path('admin/categories/', views.AdminServiceCategoryView.as_view(), name='admin_category_list'),
    path('admin/categories/<int:pk>/', views.AdminServiceCategoryDetailView.as_view(), name='admin_category_detail'),
    path('admin/', views.AdminServiceView.as_view(), name='admin_service_list'),
    path('admin/<int:pk>/', views.AdminServiceDetailView.as_view(), name='admin_service_detail'),
    path('admin/<int:service_id>/variants/', views.AdminServiceVariantView.as_view(), name='admin_variant_list'),
    path('admin/variants/<int:pk>/', views.AdminServiceVariantDetailView.as_view(), name='admin_variant_detail'),
    path('admin/<int:service_id>/pricing/', views.AdminPricingRuleView.as_view(), name='admin_pricing_list'),
    path('admin/pricing/<int:pk>/', views.AdminPricingRuleDetailView.as_view(), name='admin_pricing_detail'),
] 