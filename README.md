# Dry Cleaning Service - Django Backend

A comprehensive Django backend for a dry cleaning service with user management, order tracking, payment processing, and notification systems.

## Features

### 🔐 User Authentication & Management
- User registration and login
- Password reset functionality
- User profile management
- Role-based access control

### 📦 Order Management System
- Create and track orders
- Pickup and delivery scheduling
- Order status tracking (picked up, in-process, delivered)
- Order history and analytics
- Bulk order estimation

### 💳 Payment Processing
- Multiple payment gateway integration:
  - Stripe
  - Razorpay
  - PayPal (ready for integration)
- Payment verification and refund management
- Payment method management

### 🔔 Notification System
- Email notifications using Django's email backend
- SMS notifications using Twilio
- Customizable notification templates
- Notification preferences management
- Automated reminders for pickup and delivery

### 🛠️ Admin Dashboard
- Comprehensive admin interface
- Order management and status updates
- Service and pricing management
- User management
- Payment tracking
- Notification management

### 📊 API Endpoints
- RESTful API for frontend integration
- Comprehensive serializers for data validation
- Authentication and permission controls
- API documentation with CoreAPI

## Technology Stack

- **Backend Framework**: Django 4.2+
- **API Framework**: Django REST Framework
- **Task Queue**: Celery with Redis
- **Payment Gateways**: Stripe, Razorpay
- **SMS Service**: Twilio
- **Database**: SQLite (development) / PostgreSQL (production)
- **Documentation**: CoreAPI

## Installation & Setup

### Prerequisites
- Python 3.8+
- Redis (for Celery)
- Virtual environment

### 1. Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd dryclean

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the project root with the following variables:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3

# Email Settings
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

# Twilio Settings
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-phone

# Redis Settings
REDIS_URL=redis://localhost:6379/0

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
```

### 3. Database Setup
```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 4. Start Services
```bash
# Start Django development server
python manage.py runserver

# Start Redis (in a separate terminal)
redis-server

# Start Celery worker (in a separate terminal)
celery -A dryclean_project worker -l info

# Start Celery beat for scheduled tasks (in a separate terminal)
celery -A dryclean_project beat -l info
```

## API Documentation

### Authentication Endpoints
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/change-password/` - Change password
- `POST /api/auth/reset-password/` - Request password reset
- `POST /api/auth/reset-password-confirm/` - Confirm password reset

### User Management
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile
- `GET /api/auth/dashboard/` - User dashboard data

### Services
- `GET /api/services/categories/` - List service categories
- `GET /api/services/` - List all services
- `GET /api/services/{id}/` - Get service details
- `POST /api/services/estimate/` - Get service estimate
- `POST /api/services/bulk-estimate/` - Bulk estimation

### Orders
- `GET /api/orders/` - List user orders
- `POST /api/orders/` - Create new order
- `GET /api/orders/{id}/` - Get order details
- `PUT /api/orders/{id}/status/` - Update order status
- `GET /api/orders/{id}/track/` - Track order
- `POST /api/orders/{id}/cancel/` - Cancel order

### Payments
- `GET /api/payments/` - List payments
- `POST /api/payments/` - Create payment
- `GET /api/payments/{id}/` - Get payment details
- `POST /api/payments/stripe/create-intent/` - Create Stripe payment intent
- `POST /api/payments/razorpay/create-order/` - Create Razorpay order
- `POST /api/payments/verify/` - Verify payment

### Notifications
- `GET /api/notifications/` - List notifications
- `GET /api/notifications/{id}/` - Get notification details
- `POST /api/notifications/{id}/mark-read/` - Mark notification as read
- `GET /api/notifications/preferences/` - Get notification preferences
- `PUT /api/notifications/preferences/` - Update notification preferences

## Admin Interface

Access the Django admin interface at `http://localhost:8000/admin/` with your superuser credentials.

### Admin Features
- **User Management**: View and manage user accounts
- **Order Management**: Track and update order statuses
- **Service Management**: Configure services and pricing
- **Payment Tracking**: Monitor payments and refunds
- **Notification Management**: Send notifications and manage templates

## Project Structure

```
dryclean/
├── dryclean_project/          # Main Django project
│   ├── settings.py           # Project settings
│   ├── urls.py              # Main URL configuration
│   ├── celery.py            # Celery configuration
│   └── wsgi.py              # WSGI configuration
├── accounts/                 # User authentication app
├── services/                 # Services and pricing app
├── orders/                   # Order management app
├── payments/                 # Payment processing app
├── notifications/            # Notification system app
├── static/                   # Static files
├── media/                    # User uploaded files
├── templates/                # Django templates
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
└── README.md                # This file
```

## Development

### Running Tests
```bash
python manage.py test
```

### Code Quality
```bash
# Install development dependencies
pip install flake8 black isort

# Format code
black .
isort .

# Lint code
flake8 .
```

### Database Management
```bash
# Create new migration
python manage.py makemigrations <app_name>

# Apply migrations
python manage.py migrate

# Reset database (development only)
python manage.py flush
```

## Production Deployment

### Environment Variables
Update the `.env` file with production settings:
- Set `DEBUG=False`
- Use strong `SECRET_KEY`
- Configure production database
- Set up production email settings
- Configure production payment keys

### Static Files
```bash
python manage.py collectstatic
```

### Database
- Use PostgreSQL for production
- Configure database backups
- Set up database migrations

### Security
- Use HTTPS
- Configure CORS properly
- Set up proper authentication
- Regular security updates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository. 