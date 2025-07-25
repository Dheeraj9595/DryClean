#!/usr/bin/env python
"""
Simple Django script to create fresh test data for the dry cleaning project.
Run with: python create_fresh_test_data.py
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

def create_fresh_test_data():
    """Create fresh test data"""
    print("🚀 Creating fresh test data for Dry Cleaning API...")
    print("=" * 50)
    
    # Clear existing data (optional - be careful in production!)
    print("Clearing existing test data...")
    User.objects.filter(username__in=['john_doe', 'jane_smith', 'mike_wilson']).delete()
    ServiceCategory.objects.all().delete()
    Service.objects.all().delete()
    ServiceVariant.objects.all().delete()
    PricingRule.objects.all().delete()
    Order.objects.all().delete()
    Payment.objects.all().delete()
    PaymentMethod.objects.all().delete()
    Notification.objects.all().delete()
    EmailTemplate.objects.all().delete()
    SMSTemplate.objects.all().delete()
    NotificationPreference.objects.all().delete()
    
    print("✅ Existing data cleared")
    print()
    
    # Create admin user if not exists
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
        print(f"✅ Created admin user: {admin_user.username}")
    
    # Create test users
    print("Creating test users...")
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
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            password='testpass123'
        )
        
        # Update user profile (already created by signal)
        user.userprofile.phone_number = user_data['phone']
        user.userprofile.address = user_data['address']
        user.userprofile.city = user_data['city']
        user.userprofile.state = user_data['state']
        user.userprofile.pincode = user_data['zip_code']
        user.userprofile.save()
        
        created_users.append(user)
        print(f"✅ Created user: {user.username}")
    
    # Create service categories
    print("\nCreating service categories...")
    categories_data = [
        {'name': 'Dry Cleaning', 'description': 'Professional dry cleaning services', 'icon': '🧥'},
        {'name': 'Laundry', 'description': 'Wash and fold laundry services', 'icon': '👕'},
        {'name': 'Pressing', 'description': 'Professional pressing services', 'icon': '👔'},
        {'name': 'Alterations', 'description': 'Clothing alterations', 'icon': '✂️'},
        {'name': 'Stain Removal', 'description': 'Specialized stain removal', 'icon': '🧽'}
    ]
    
    categories = []
    for cat_data in categories_data:
        category = ServiceCategory.objects.create(**cat_data)
        categories.append(category)
        print(f"✅ Created category: {category.name}")
    
    # Create services
    print("\nCreating services...")
    services_data = [
        {'name': 'Suit Dry Cleaning', 'category': categories[0], 'description': 'Professional suit cleaning', 'base_price': 15.00},
        {'name': 'Shirt Laundry', 'category': categories[1], 'description': 'Wash and press shirts', 'base_price': 3.50},
        {'name': 'Dress Dry Cleaning', 'category': categories[0], 'description': 'Delicate dress cleaning', 'base_price': 12.00},
        {'name': 'Pants Pressing', 'category': categories[2], 'description': 'Professional pants pressing', 'base_price': 5.00},
        {'name': 'Stain Treatment', 'category': categories[4], 'description': 'Specialized stain removal', 'base_price': 8.00}
    ]
    
    services = []
    for service_data in services_data:
        service = Service.objects.create(**service_data)
        services.append(service)
        print(f"✅ Created service: {service.name}")
    
    # Create service variants
    print("\nCreating service variants...")
    variants_data = [
        {'service': services[0], 'name': '2-Piece Suit', 'price_modifier': 0.00},
        {'service': services[0], 'name': '3-Piece Suit', 'price_modifier': 5.00},
        {'service': services[1], 'name': 'Regular Shirt', 'price_modifier': 0.00},
        {'service': services[1], 'name': 'Silk Shirt', 'price_modifier': 2.00},
        {'service': services[2], 'name': 'Casual Dress', 'price_modifier': 0.00},
        {'service': services[2], 'name': 'Formal Dress', 'price_modifier': 3.00}
    ]
    
    variants = []
    for variant_data in variants_data:
        variant = ServiceVariant.objects.create(**variant_data)
        variants.append(variant)
        print(f"✅ Created variant: {variant.name}")
    
    # Create pricing rules
    print("\nCreating pricing rules...")
    rules_data = [
        {'service': services[0], 'min_quantity': 1, 'price_per_unit': 20.00},
        {'service': services[1], 'min_quantity': 10, 'price_per_unit': 2.50},
        {'service': services[2], 'min_quantity': 1, 'price_per_unit': 15.00}
    ]
    
    rules = []
    for rule_data in rules_data:
        rule = PricingRule.objects.create(**rule_data)
        rules.append(rule)
        print(f"✅ Created pricing rule: {rule}")
    
    # Create orders
    print("\nCreating test orders...")
    order_statuses = ['pending', 'confirmed', 'picked_up', 'in_process', 'ready', 'delivered']
    orders = []
    
    for user in created_users:
        for j in range(random.randint(2, 3)):
            status = random.choice(order_statuses)
            created_date = timezone.now() - timedelta(days=random.randint(1, 30))
            pickup_date = created_date + timedelta(days=1)
            delivery_date = pickup_date + timedelta(days=random.randint(1, 3))
            
            order = Order(
                customer=user,
                status=status,
                order_type='pickup',
                pickup_address=user.userprofile.address,
                pickup_date=pickup_date.date(),
                pickup_time_slot='9:00 AM - 12:00 PM',
                delivery_address=user.userprofile.address,
                delivery_date=delivery_date.date(),
                delivery_time_slot='2:00 PM - 5:00 PM',
                special_instructions=f"Test order {j+1} for {user.first_name}",
                created_at=created_date
            )
            # Save without triggering calculate_totals
            order.save(force_insert=True)
            
            # Create pickup schedule
            PickupSchedule.objects.create(
                order=order,
                scheduled_date=pickup_date.date(),
                scheduled_time_slot='9:00 AM - 12:00 PM'
            )
            
            # Create delivery schedule
            DeliverySchedule.objects.create(
                order=order,
                scheduled_date=delivery_date.date(),
                scheduled_time_slot='2:00 PM - 5:00 PM'
            )
            
            # Create order items
            num_items = random.randint(1, 3)
            total_amount = 0.00
            
            for k in range(num_items):
                service = random.choice(services)
                quantity = random.randint(1, 2)
                urgency = random.choice(['normal', 'express'])
                
                unit_price = service.base_price
                if urgency == 'express':
                    unit_price += 5.00
                
                total_price = unit_price * quantity
                total_amount += total_price
                
                item = OrderItem.objects.create(
                    order=order,
                    service=service,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price,
                    special_instructions=f"Item {k+1} instructions"
                )
            
            order.total_amount = total_amount
            order.save()
            
            # Create status history
            OrderStatusHistory.objects.create(
                order=order,
                status=status,
                notes=f"Order {status}"
            )
            
            orders.append(order)
            print(f"✅ Created order: {order.order_number} for {user.username}")
    
    # Create payments
    print("\nCreating test payments...")
    payments = []
    
    for user in created_users:
        # Create payment method for user
        payment_method = PaymentMethod.objects.create(
            user=user,
            payment_method='stripe',
            card_last4='1234',
            card_brand='visa',
            card_exp_month=12,
            card_exp_year=2025,
            is_default=True,
            is_active=True
        )
        print(f"✅ Created payment method for {user.username}")
    
    for order in orders:
        if order.status in ['confirmed', 'picked_up', 'in_process', 'ready', 'delivered']:
            payment_method_type = random.choice(['stripe', 'razorpay', 'cod'])
            payment_status = random.choice(['pending', 'completed', 'failed'])
            
            payment = Payment.objects.create(
                order=order,
                user=order.customer,
                payment_method=payment_method_type,
                amount=order.total_amount,
                status=payment_status,
                currency='USD'
            )
            
            if payment_status == 'completed':
                PaymentTransaction.objects.create(
                    payment=payment,
                    transaction_id=f"TXN_{payment.id}_{random.randint(1000, 9999)}",
                    amount=payment.amount,
                    status='success'
                )
            
            payments.append(payment)
            print(f"✅ Created payment: ${payment.amount} for order {order.order_number}")
    
    # Create notifications
    print("\nCreating test notifications...")
    notifications = []
    
    for user in created_users:
        # Create notification preferences
        NotificationPreference.objects.create(
            user=user,
            email_order_confirmation=True,
            email_status_updates=True,
            email_pickup_reminder=True,
            email_delivery_notification=True,
            email_promotional=False,
            sms_order_confirmation=True,
            sms_status_updates=True,
            sms_pickup_reminder=True,
            sms_delivery_notification=True,
            sms_promotional=False,
            push_order_confirmation=True,
            push_status_updates=True,
            push_pickup_reminder=True,
            push_delivery_notification=True,
            push_promotional=False
        )
        
        # Create notifications for user's orders
        user_orders = Order.objects.filter(customer=user)
        for order in user_orders:
            notification_type = random.choice(['order_confirmation', 'pickup_reminder', 'delivery_notification', 'status_update'])
            
            notification = Notification.objects.create(
                user=user,
                title=f"Order {order.order_number} Update",
                message=f"Your order {order.order_number} has been {order.status}",
                notification_type=notification_type,
                is_read=random.choice([True, False]),
                order=order
            )
            
            notifications.append(notification)
            print(f"✅ Created notification: {notification.title}")
    
    # Create email templates
    print("\nCreating email templates...")
    email_templates_data = [
        {
            'name': 'Order Confirmation',
            'subject': 'Order Confirmed - {{order_number}}',
            'body': 'Dear {{customer_name}}, Your order {{order_number}} has been confirmed.',
            'is_active': True
        },
        {
            'name': 'Pickup Reminder',
            'subject': 'Pickup Reminder - {{order_number}}',
            'body': 'Dear {{customer_name}}, Your order {{order_number}} is scheduled for pickup today.',
            'is_active': True
        },
        {
            'name': 'Delivery Notification',
            'subject': 'Order Ready for Delivery - {{order_number}}',
            'body': 'Dear {{customer_name}}, Your order {{order_number}} is ready for delivery.',
            'is_active': True
        }
    ]
    
    email_templates = []
    for template_data in email_templates_data:
        template = EmailTemplate.objects.create(**template_data)
        email_templates.append(template)
        print(f"✅ Created email template: {template.name}")
    
    # Create SMS templates
    print("\nCreating SMS templates...")
    sms_templates_data = [
        {
            'name': 'Order Confirmation SMS',
            'message': 'Order {{order_number}} confirmed. Pickup: {{pickup_date}} at {{pickup_time}}.',
            'is_active': True
        },
        {
            'name': 'Pickup Reminder SMS',
            'message': 'Reminder: Order {{order_number}} pickup today at {{pickup_time}}.',
            'is_active': True
        },
        {
            'name': 'Delivery Notification SMS',
            'message': 'Order {{order_number}} ready! Delivery: {{delivery_date}} at {{delivery_time}}.',
            'is_active': True
        }
    ]
    
    sms_templates = []
    for template_data in sms_templates_data:
        template = SMSTemplate.objects.create(**template_data)
        sms_templates.append(template)
        print(f"✅ Created SMS template: {template.name}")
    
    print("\n" + "=" * 50)
    print("✅ Fresh test data creation completed successfully!")
    print()
    print("📊 Summary:")
    print(f"   👥 Users: {len(created_users)}")
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
    print("🎉 Your API is now populated with fresh test data!")

if __name__ == '__main__':
    create_fresh_test_data() 