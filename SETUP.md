# Dry Cleaning Django Project - Setup Guide

## 🎉 Project Successfully Created!

Your comprehensive Django backend for the dry cleaning service has been successfully created and is ready to use.

## ✅ What's Been Completed

### 1. **Project Structure**
- ✅ Django project with 5 modular apps
- ✅ Virtual environment setup
- ✅ All dependencies installed
- ✅ Database migrations applied
- ✅ Superuser created

### 2. **Core Features Implemented**
- ✅ **User Authentication System** (accounts app)
- ✅ **Order Management System** (orders app)
- ✅ **Service & Pricing Management** (services app)
- ✅ **Payment Processing** (payments app)
- ✅ **Notification System** (notifications app)
- ✅ **Admin Dashboard** (customized for all apps)

### 3. **API Endpoints**
- ✅ RESTful API with Django REST Framework
- ✅ Comprehensive serializers for data validation
- ✅ Authentication and permission controls
- ✅ API documentation with CoreAPI

### 4. **Advanced Features**
- ✅ Celery integration for background tasks
- ✅ Redis configuration for task queue
- ✅ Multiple payment gateway support (Stripe, Razorpay)
- ✅ Email and SMS notification system
- ✅ Order tracking and status management

## 🚀 Quick Start

### 1. **Start the Development Server**
```bash
# Activate virtual environment
source venv/bin/activate

# Start Django server
python manage.py runserver
```

### 2. **Access the Application**
- **API Root**: http://localhost:8000/
- **Health Check**: http://localhost:8000/health/
- **Admin Interface**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/docs/

### 3. **Admin Login**
- **Username**: admin
- **Email**: admin@dryclean.com
- **Password**: (you'll need to set this)

## 🔧 Environment Configuration

### Required Environment Variables
Create a `.env` file in the project root:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3

# Email Settings (for notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Payment Gateway Keys
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-key
STRIPE_SECRET_KEY=sk_test_your-stripe-secret
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret

# Twilio Settings (for SMS notifications)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-phone

# Redis Settings (for Celery)
REDIS_URL=redis://localhost:6379/0

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
```

## 📊 API Endpoints Overview

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/change-password/` - Change password
- `POST /api/auth/reset-password/` - Request password reset

### User Management
- `GET /api/accounts/profile/` - Get user profile
- `PUT /api/accounts/profile/` - Update user profile
- `GET /api/accounts/dashboard/` - User dashboard data

### Services
- `GET /api/services/categories/` - List service categories
- `GET /api/services/` - List all services
- `GET /api/services/{id}/` - Get service details
- `POST /api/services/estimate/` - Get service estimate

### Orders
- `GET /api/orders/` - List user orders
- `POST /api/orders/` - Create new order
- `GET /api/orders/{id}/` - Get order details
- `PUT /api/orders/{id}/status/` - Update order status
- `GET /api/orders/{id}/track/` - Track order

### Payments
- `GET /api/payments/` - List payments
- `POST /api/payments/` - Create payment
- `POST /api/payments/stripe/create-intent/` - Create Stripe payment intent
- `POST /api/payments/razorpay/create-order/` - Create Razorpay order

### Notifications
- `GET /api/notifications/` - List notifications
- `POST /api/notifications/{id}/mark-read/` - Mark notification as read
- `GET /api/notifications/preferences/` - Get notification preferences

## 🛠️ Additional Setup (Optional)

### 1. **Start Celery for Background Tasks**
```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery worker
celery -A dryclean_project worker -l info

# Terminal 3: Start Celery beat (for scheduled tasks)
celery -A dryclean_project beat -l info
```

### 2. **Set Admin Password**
```bash
python manage.py changepassword admin
```

### 3. **Create Sample Data**
You can create sample data through the Django admin interface or by creating management commands.

## 🔗 Frontend Integration

The API is designed to work with your existing frontend at:
`https://anushri-choubey04.github.io/DryCleaning/`

### CORS Configuration
The project is configured to allow requests from your frontend domain. Update the `FRONTEND_URL` in your `.env` file if needed.

## 📝 Next Steps

### 1. **Configure Payment Gateways**
- Set up Stripe account and get API keys
- Set up Razorpay account and get API keys
- Update the `.env` file with your keys

### 2. **Configure Email/SMS**
- Set up Gmail SMTP or other email provider
- Set up Twilio account for SMS notifications
- Update the `.env` file with your credentials

### 3. **Production Deployment**
- Set up PostgreSQL database
- Configure production settings
- Set up SSL/HTTPS
- Configure proper CORS settings

### 4. **Testing**
- Test all API endpoints
- Test payment integrations
- Test notification system
- Test order flow end-to-end

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure virtual environment is activated
2. **Database Errors**: Run `python manage.py migrate`
3. **Payment Errors**: Check API keys in `.env` file
4. **Email Errors**: Verify SMTP settings
5. **Celery Errors**: Ensure Redis is running

### Useful Commands
```bash
# Check Django status
python manage.py check

# List all URLs
python manage.py show_urls

# Reset database (development only)
python manage.py flush

# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## 📞 Support

If you encounter any issues:
1. Check the Django debug output
2. Review the logs in the terminal
3. Verify all environment variables are set
4. Ensure all dependencies are installed

## 🎯 Project Status

✅ **Complete**: Core backend functionality
✅ **Complete**: API endpoints
✅ **Complete**: Admin interface
✅ **Complete**: Database models
✅ **Complete**: Authentication system
✅ **Complete**: Payment integration structure
✅ **Complete**: Notification system structure

🔄 **Ready for**: Frontend integration
🔄 **Ready for**: Payment gateway configuration
🔄 **Ready for**: Production deployment

---

**Your Django dry cleaning backend is ready to use! 🚀** 