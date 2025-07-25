#!/usr/bin/env python
"""
Django management command to create test data for the dry cleaning project.
Run with: python manage.py create_test_data
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dryclean_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import UserProfile
from services.models import ServiceCategory, Service, ServiceVariant, PricingRule
from orders.models import Order, OrderItem, OrderStatusHistory, PickupSchedule, DeliverySchedule
from payments.models import Payment, PaymentMethod, PaymentTransaction, Refund
from notifications.models import Notification, EmailTemplate, SMSTemplate, NotificationPreference

def create_users():
    """Create test users"""
    print("Creating test users...")
    
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@dryclean.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"Created admin user: {admin_user.username}")
    
    # Create regular users
    users_data = [
        {
            'username': 'john_doe',
            'email': 'john@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+1234567890',
            'address': '123 Main Street',
            'city': 'New York',
            'state': 'NY',
            'zip_code': '10001'
        },
        {
            'username': 'jane_smith',
            'email': 'jane@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'phone': '+1234567891',
            'address': '456 Oak Avenue',
            'city': 'Los Angeles',
            'state': 'CA',
            'zip_code': '90210'
        },
        {
            'username': 'mike_wilson',
            'email': 'mike@example.com',
            'first_name': 'Mike',
            'last_name': 'Wilson',
            'phone': '+1234567892',
            'address': '789 Pine Road',
            'city': 'Chicago',
            'state': 'IL',
            'zip_code': '60601'
        }
    ]
    
    created_users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name']
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            
            # Create user profile
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'phone': user_data['phone'],
                    'address': user_data['address'],
                    'city': user_data['city'],
                    'state': user_data['state'],
                    'zip_code': user_data['zip_code']
                }
            )
            created_users.append(user)
            print(f"Created user: {user.username}")
    
    return created_users

def create_service_categories():
    """Create service categories"""
    print("Creating service categories...")
    
    categories_data = [
        {
            'name': 'Dry Cleaning',
            'description': 'Professional dry cleaning services for all types of garments',
            'icon': '🧥'
        },
        {
            'name': 'Laundry',
            'description': 'Wash and fold laundry services',
            'icon': '👕'
        },
        {
            'name': 'Pressing',
            'description': 'Professional pressing and ironing services',
            'icon': '👔'
        },
        {
            'name': 'Alterations',
            'description': 'Clothing alterations and repairs',
            'icon': '✂️'
        },
        {
            'name': 'Stain Removal',
            'description': 'Specialized stain removal services',
            'icon': '🧽'
        }
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = ServiceCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f"Created category: {category.name}")
        categories.append(category)
    
    return categories

def create_services(categories):
    """Create services"""
    print("Creating services...")
    
    services_data = [
        {
            'name': 'Suit Dry Cleaning',
            'category': categories[0],  # Dry Cleaning
            'description': 'Professional dry cleaning for suits and formal wear',
            'base_price': 15.00
        },
        {
            'name': 'Shirt Laundry',
            'category': categories[1],  # Laundry
            'description': 'Wash, dry, and press shirts',
            'base_price': 3.50
        },
        {
            'name': 'Dress Dry Cleaning',
            'category': categories[0],  # Dry Cleaning
            'description': 'Delicate dry cleaning for dresses',
            'base_price': 12.00
        },
        {
            'name': 'Pants Pressing',
            'category': categories[2],  # Pressing
            'description': 'Professional pressing for pants',
            'base_price': 5.00
        },
        {
            'name': 'Stain Treatment',
            'category': categories[4],  # Stain Removal
            'description': 'Specialized stain removal treatment',
            'base_price': 8.00
        }
    ]
    
    services = []
    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            name=service_data['name'],
            category=service_data['category'],
            defaults=service_data
        )
        if created:
            print(f"Created service: {service.name}")
        services.append(service)
    
    return services

def create_service_variants(services):
    """Create service variants"""
    print("Creating service variants...")
    
    variants_data = [
        # Suit variants
        {
            'service': services[0],  # Suit Dry Cleaning
            'name': '2-Piece Suit',
            'price_modifier': 0.00
        },
        {
            'service': services[0],  # Suit Dry Cleaning
            'name': '3-Piece Suit',
            'price_modifier': 5.00
        },
        # Shirt variants
        {
            'service': services[1],  # Shirt Laundry
            'name': 'Regular Shirt',
            'price_modifier': 0.00
        },
        {
            'service': services[1],  # Shirt Laundry
            'name': 'Silk Shirt',
            'price_modifier': 2.00
        },
        # Dress variants
        {
            'service': services[2],  # Dress Dry Cleaning
            'name': 'Casual Dress',
            'price_modifier': 0.00
        },
        {
            'service': services[2],  # Dress Dry Cleaning
            'name': 'Formal Dress',
            'price_modifier': 3.00
        }
    ]
    
    variants = []
    for variant_data in variants_data:
        variant, created = ServiceVariant.objects.get_or_create(
            service=variant_data['service'],
            name=variant_data['name'],
            defaults=variant_data
        )
        if created:
            print(f"Created variant: {variant.name} for {variant.service.name}")
        variants.append(variant)
    
    return variants

def create_pricing_rules(services):
    """Create pricing rules"""
    print("Creating pricing rules...")
    
    rules_data = [
        {
            'service': services[0],  # Suit Dry Cleaning
            'variant': None,
            'min_quantity': 1,
            'max_quantity': None,
            'price_per_unit': 20.00,  # Express price
        },
        {
            'service': services[0],  # Suit Dry Cleaning
            'variant': None,
            'min_quantity': 1,
            'max_quantity': None,
            'price_per_unit': 15.00,  # Standard price
        },
        {
            'service': services[1],  # Shirt Laundry
            'variant': None,
            'min_quantity': 10,
            'max_quantity': None,
            'price_per_unit': 2.50,  # Bulk discount price
        },
        {
            'service': services[2],  # Dress Dry Cleaning
            'variant': None,
            'min_quantity': 1,
            'max_quantity': None,
            'price_per_unit': 15.00,  # Express price
        }
    ]
    
    rules = []
    for rule_data in rules_data:
        rule, created = PricingRule.objects.get_or_create(
            service=rule_data['service'],
            min_quantity=rule_data['min_quantity'],
            price_per_unit=rule_data['price_per_unit'],
            defaults=rule_data
        )
        if created:
            print(f"Created pricing rule: {rule}")
        rules.append(rule)
    
    return rules

def create_orders(users, services):
    """Create test orders"""
    print("Creating test orders...")
    
    order_statuses = ['pending', 'confirmed', 'picked_up', 'in_process', 'ready', 'delivered']
    
    orders = []
    for i, user in enumerate(users):
        # Create 2-3 orders per user
        for j in range(random.randint(2, 3)):
            # Random status
            status = random.choice(order_statuses)
            
            # Random dates
            created_date = timezone.now() - timedelta(days=random.randint(1, 30))
            pickup_date = created_date + timedelta(days=1)
            delivery_date = pickup_date + timedelta(days=random.randint(1, 3))
            
            order = Order.objects.create(
                user=user,
                status=status,
                total_amount=0.00,  # Will be calculated
                special_instructions=f"Test order {j+1} for {user.first_name}",
                created_at=created_date
            )
            
            # Create pickup schedule
            PickupSchedule.objects.create(
                order=order,
                address=user.userprofile.address,
                city=user.userprofile.city,
                state=user.userprofile.state,
                zip_code=user.userprofile.zip_code,
                phone=user.userprofile.phone,
                scheduled_date=pickup_date,
                scheduled_time=datetime.strptime('10:00:00', '%H:%M:%S').time()
            )
            
            # Create delivery schedule
            DeliverySchedule.objects.create(
                order=order,
                address=user.userprofile.address,
                city=user.userprofile.city,
                state=user.userprofile.state,
                zip_code=user.userprofile.zip_code,
                phone=user.userprofile.phone,
                scheduled_date=delivery_date,
                scheduled_time=datetime.strptime('14:00:00', '%H:%M:%S').time()
            )
            
            # Create order items
            num_items = random.randint(1, 3)
            total_amount = 0.00
            
            for k in range(num_items):
                service = random.choice(services)
                quantity = random.randint(1, 2)
                urgency = random.choice(['normal', 'express'])
                
                item = OrderItem.objects.create(
                    order=order,
                    service=service,
                    quantity=quantity,
                    urgency=urgency,
                    special_instructions=f"Item {k+1} instructions"
                )
                
                # Calculate item price
                item_price = service.base_price * quantity
                if urgency == 'express':
                    item_price += 5.00  # Express fee
                
                total_amount += item_price
            
            # Update order total
            order.total_amount = total_amount
            order.save()
            
            # Create status history
            OrderStatusHistory.objects.create(
                order=order,
                status=status,
                notes=f"Order {status}",
                timestamp=created_date
            )
            
            orders.append(order)
            print(f"Created order: {order.order_number} for {user.username}")
    
    return orders

def create_payments(orders):
    """Create test payments"""
    print("Creating test payments...")
    
    # Create payment methods for each user
    payment_methods = []
    for user in User.objects.filter(is_staff=False):
        # Create a credit card payment method for each user
        method, created = PaymentMethod.objects.get_or_create(
            user=user,
            payment_method='stripe',
            card_last4='1234',
            card_brand='visa',
            card_exp_month=12,
            card_exp_year=2025,
            is_default=True,
            is_active=True
        )
        if created:
            print(f"Created payment method for {user.username}")
        payment_methods.append(method)
    
    payments = []
    for order in orders:
        if order.status in ['confirmed', 'picked_up', 'in_process', 'ready', 'delivered']:
            payment_method_type = random.choice(['stripe', 'razorpay', 'cod'])
            payment_status = random.choice(['pending', 'completed', 'failed'])
            
            payment = Payment.objects.create(
                order=order,
                user=order.user,
                payment_method=payment_method_type,
                amount=order.total_amount,
                status=payment_status,
                currency='USD'
            )
            
            # Create payment transaction
            if payment_status == 'completed':
                PaymentTransaction.objects.create(
                    payment=payment,
                    transaction_id=f"TXN_{payment.id}_{random.randint(1000, 9999)}",
                    amount=payment.amount,
                    status='success',
                    gateway='test_gateway'
                )
            
            payments.append(payment)
            print(f"Created payment: ${payment.amount} for order {order.order_number}")
    
    return payments

def create_notifications(users, orders):
    """Create test notifications"""
    print("Creating test notifications...")
    
    notification_types = ['order_confirmation', 'pickup_reminder', 'delivery_notification', 'status_update']
    
    notifications = []
    for user in users:
        # Create notification preferences
        NotificationPreference.objects.get_or_create(
            user=user,
            defaults={
                'email_notifications': True,
                'sms_notifications': True,
                'push_notifications': True,
                'order_updates': True,
                'promotional_emails': False
            }
        )
        
        # Create notifications for user's orders
        user_orders = Order.objects.filter(user=user)
        for order in user_orders:
            notification_type = random.choice(notification_types)
            
            notification = Notification.objects.create(
                user=user,
                title=f"Order {order.order_number} Update",
                message=f"Your order {order.order_number} has been {order.status}",
                notification_type=notification_type,
                is_read=random.choice([True, False]),
                related_order=order
            )
            
            notifications.append(notification)
            print(f"Created notification: {notification.title}")
    
    return notifications

def create_email_templates():
    """Create email templates"""
    print("Creating email templates...")
    
    templates_data = [
        {
            'name': 'Order Confirmation',
            'subject': 'Order Confirmed - {{order_number}}',
            'body': '''
Dear {{customer_name}},

Your order {{order_number}} has been confirmed and is scheduled for pickup on {{pickup_date}}.

Order Details:
- Total Amount: ${{total_amount}}
- Pickup Date: {{pickup_date}}
- Delivery Date: {{delivery_date}}

Thank you for choosing our service!

Best regards,
Dry Clean Team
            ''',
            'is_active': True
        },
        {
            'name': 'Pickup Reminder',
            'subject': 'Pickup Reminder - {{order_number}}',
            'body': '''
Dear {{customer_name}},

This is a reminder that your order {{order_number}} is scheduled for pickup today at {{pickup_time}}.

Please ensure someone is available at the pickup address.

Thank you!

Best regards,
Dry Clean Team
            ''',
            'is_active': True
        },
        {
            'name': 'Delivery Notification',
            'subject': 'Order Ready for Delivery - {{order_number}}',
            'body': '''
Dear {{customer_name}},

Your order {{order_number}} is ready and will be delivered on {{delivery_date}} at {{delivery_time}}.

Thank you for your patience!

Best regards,
Dry Clean Team
            ''',
            'is_active': True
        }
    ]
    
    templates = []
    for template_data in templates_data:
        template, created = EmailTemplate.objects.get_or_create(
            name=template_data['name'],
            defaults=template_data
        )
        if created:
            print(f"Created email template: {template.name}")
        templates.append(template)
    
    return templates

def create_sms_templates():
    """Create SMS templates"""
    print("Creating SMS templates...")
    
    templates_data = [
        {
            'name': 'Order Confirmation SMS',
            'message': 'Order {{order_number}} confirmed. Pickup: {{pickup_date}} at {{pickup_time}}. Thank you!',
            'is_active': True
        },
        {
            'name': 'Pickup Reminder SMS',
            'message': 'Reminder: Order {{order_number}} pickup today at {{pickup_time}}. Please be available.',
            'is_active': True
        },
        {
            'name': 'Delivery Notification SMS',
            'message': 'Order {{order_number}} ready! Delivery: {{delivery_date}} at {{delivery_time}}.',
            'is_active': True
        }
    ]
    
    templates = []
    for template_data in templates_data:
        template, created = SMSTemplate.objects.get_or_create(
            name=template_data['name'],
            defaults=template_data
        )
        if created:
            print(f"Created SMS template: {template.name}")
        templates.append(template)
    
    return templates

def main():
    """Main function to create all test data"""
    print("🚀 Creating test data for Dry Cleaning API...")
    print("=" * 50)
    
    try:
        # Create users
        users = create_users()
        print()
        
        # Create service categories
        categories = create_service_categories()
        print()
        
        # Create services
        services = create_services(categories)
        print()
        
        # Create service variants
        variants = create_service_variants(services)
        print()
        
        # Create pricing rules
        rules = create_pricing_rules(services)
        print()
        
        # Create orders
        orders = create_orders(users, services)
        print()
        
        # Create payments
        payments = create_payments(orders)
        print()
        
        # Create notifications
        notifications = create_notifications(users, orders)
        print()
        
        # Create email templates
        email_templates = create_email_templates()
        print()
        
        # Create SMS templates
        sms_templates = create_sms_templates()
        print()
        
        print("=" * 50)
        print("✅ Test data creation completed successfully!")
        print()
        print("📊 Summary:")
        print(f"   👥 Users: {len(users)}")
        print(f"   📂 Categories: {len(categories)}")
        print(f"   🛠️ Services: {len(services)}")
        print(f"   🔄 Variants: {len(variants)}")
        print(f"   💰 Pricing Rules: {len(rules)}")
        print(f"   📦 Orders: {len(orders)}")
        print(f"   💳 Payments: {len(payments)}")
        print(f"   🔔 Notifications: {len(notifications)}")
        print(f"   📧 Email Templates: {len(email_templates)}")
        print(f"   📱 SMS Templates: {len(sms_templates)}")
        print()
        print("🔑 Test Credentials:")
        print("   Admin: admin / admin123")
        print("   Users: john_doe, jane_smith, mike_wilson / testpass123")
        print()
        print("🌐 API Endpoints to test:")
        print("   - http://localhost:8000/api/services/categories/")
        print("   - http://localhost:8000/api/services/")
        print("   - http://localhost:8000/api/auth/login/")
        print("   - http://localhost:8000/api/orders/ (after login)")
        print()
        print("🎉 Your API is now populated with test data!")
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 