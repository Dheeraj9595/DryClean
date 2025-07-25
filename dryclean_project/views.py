from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny


@csrf_exempt
def root_view(request):
    """
    Root view providing API information and links
    """
    return JsonResponse({
        'message': 'Dry Cleaning Service API',
        'version': '1.0.0',
        'endpoints': {
            'authentication': '/api/auth/',
            'services': '/api/services/',
            'orders': '/api/orders/',
            'payments': '/api/payments/',
            'notifications': '/api/notifications/',
            'admin': '/admin/',
            'api_docs': '/api/docs/',
            'api_overview': '/api-overview/',
        },
        'documentation': 'Visit /api/docs/ for interactive API documentation',
        'status': 'running'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def health_check(request):
    """
    Health check endpoint for monitoring
    """
    return Response({
        'status': 'healthy',
        'service': 'dry-cleaning-api',
        'version': '1.0.0'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def api_overview(request):
    """
    Comprehensive API overview with all endpoints
    """
    return Response({
        'message': 'Dry Cleaning Service - Complete API Overview',
        'version': '1.0.0',
        'base_url': 'http://localhost:8000',
        'authentication': {
            'note': 'Most endpoints require authentication. Use /api/auth/login/ to get a token.',
            'endpoints': {
                'register': {
                    'url': '/api/auth/register/',
                    'method': 'POST',
                    'description': 'User registration',
                    'auth_required': False
                },
                'login': {
                    'url': '/api/auth/login/',
                    'method': 'POST',
                    'description': 'User login (get token)',
                    'auth_required': False
                },
                'logout': {
                    'url': '/api/auth/logout/',
                    'method': 'POST',
                    'description': 'User logout',
                    'auth_required': True
                },
                'change_password': {
                    'url': '/api/auth/change-password/',
                    'method': 'POST',
                    'description': 'Change user password',
                    'auth_required': True
                },
                'reset_password': {
                    'url': '/api/auth/reset-password/',
                    'method': 'POST',
                    'description': 'Request password reset',
                    'auth_required': False
                },
                'profile': {
                    'url': '/api/auth/profile/',
                    'method': 'GET/PUT',
                    'description': 'Get/Update user profile',
                    'auth_required': True
                },
                'dashboard': {
                    'url': '/api/auth/dashboard/',
                    'method': 'GET',
                    'description': 'User dashboard data',
                    'auth_required': True
                }
            }
        },
        'services': {
            'endpoints': {
                'categories': {
                    'url': '/api/services/categories/',
                    'method': 'GET',
                    'description': 'List service categories',
                    'auth_required': False
                },
                'services': {
                    'url': '/api/services/',
                    'method': 'GET',
                    'description': 'List all services',
                    'auth_required': False
                },
                'service_detail': {
                    'url': '/api/services/{id}/',
                    'method': 'GET',
                    'description': 'Get service details',
                    'auth_required': False
                },
                'estimate': {
                    'url': '/api/services/estimate/',
                    'method': 'POST',
                    'description': 'Get service estimate',
                    'auth_required': False
                },
                'bulk_estimate': {
                    'url': '/api/services/bulk-estimate/',
                    'method': 'POST',
                    'description': 'Bulk service estimation',
                    'auth_required': False
                },
                'search': {
                    'url': '/api/services/search/',
                    'method': 'GET',
                    'description': 'Search services',
                    'auth_required': False
                },
                'popular': {
                    'url': '/api/services/popular/',
                    'method': 'GET',
                    'description': 'Get popular services',
                    'auth_required': False
                }
            }
        },
        'orders': {
            'endpoints': {
                'list': {
                    'url': '/api/orders/',
                    'method': 'GET',
                    'description': 'List user orders',
                    'auth_required': True
                },
                'create': {
                    'url': '/api/orders/',
                    'method': 'POST',
                    'description': 'Create new order',
                    'auth_required': True
                },
                'detail': {
                    'url': '/api/orders/{id}/',
                    'method': 'GET',
                    'description': 'Get order details',
                    'auth_required': True
                },
                'update_status': {
                    'url': '/api/orders/{id}/status/',
                    'method': 'PUT',
                    'description': 'Update order status',
                    'auth_required': True
                },
                'track': {
                    'url': '/api/orders/{id}/tracking/',
                    'method': 'GET',
                    'description': 'Track order',
                    'auth_required': True
                },
                'cancel': {
                    'url': '/api/orders/{id}/cancel/',
                    'method': 'POST',
                    'description': 'Cancel order',
                    'auth_required': True
                },
                'history': {
                    'url': '/api/orders/history/',
                    'method': 'GET',
                    'description': 'Order history',
                    'auth_required': True
                }
            }
        },
        'payments': {
            'endpoints': {
                'list': {
                    'url': '/api/payments/',
                    'method': 'GET',
                    'description': 'List payments',
                    'auth_required': True
                },
                'create': {
                    'url': '/api/payments/',
                    'method': 'POST',
                    'description': 'Create payment',
                    'auth_required': True
                },
                'detail': {
                    'url': '/api/payments/{id}/',
                    'method': 'GET',
                    'description': 'Get payment details',
                    'auth_required': True
                },
                'stripe_intent': {
                    'url': '/api/payments/stripe/create-intent/',
                    'method': 'POST',
                    'description': 'Create Stripe payment intent',
                    'auth_required': True
                },
                'razorpay_order': {
                    'url': '/api/payments/razorpay/create-order/',
                    'method': 'POST',
                    'description': 'Create Razorpay order',
                    'auth_required': True
                },
                'verify': {
                    'url': '/api/payments/verify/',
                    'method': 'POST',
                    'description': 'Verify payment',
                    'auth_required': True
                },
                'refunds': {
                    'url': '/api/payments/refunds/',
                    'method': 'GET/POST',
                    'description': 'List/Create refunds',
                    'auth_required': True
                }
            }
        },
        'notifications': {
            'endpoints': {
                'list': {
                    'url': '/api/notifications/',
                    'method': 'GET',
                    'description': 'List notifications',
                    'auth_required': True
                },
                'detail': {
                    'url': '/api/notifications/{id}/',
                    'method': 'GET',
                    'description': 'Get notification details',
                    'auth_required': True
                },
                'mark_read': {
                    'url': '/api/notifications/{id}/mark-read/',
                    'method': 'POST',
                    'description': 'Mark notification as read',
                    'auth_required': True
                },
                'preferences': {
                    'url': '/api/notifications/preferences/',
                    'method': 'GET/PUT',
                    'description': 'Get/Update notification preferences',
                    'auth_required': True
                },
                'stats': {
                    'url': '/api/notifications/stats/',
                    'method': 'GET',
                    'description': 'Get notification statistics',
                    'auth_required': True
                }
            }
        },
        'admin': {
            'url': '/admin/',
            'description': 'Django admin interface for backend management',
            'auth_required': True
        },
        'documentation': {
            'url': '/api/docs/',
            'description': 'Interactive API documentation (CoreAPI)',
            'auth_required': True
        },
        'health': {
            'url': '/health/',
            'description': 'Health check endpoint',
            'auth_required': False
        }
    }, status=status.HTTP_200_OK) 