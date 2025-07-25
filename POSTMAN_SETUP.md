# 🚀 Postman Collection Setup Guide

## 📦 **Files Created**
- `Dry_Cleaning_API.postman_collection.json` - Complete API collection
- `Dry_Cleaning_API.postman_environment.json` - Environment variables

## 🔧 **Setup Instructions**

### **1. Import Collection**
1. Open **Postman**
2. Click **"Import"** button
3. Select **"Upload Files"**
4. Choose `Dry_Cleaning_API.postman_collection.json`
5. Click **"Import"**

### **2. Import Environment**
1. Click **"Import"** again
2. Select **"Upload Files"**
3. Choose `Dry_Cleaning_API.postman_environment.json`
4. Click **"Import"**

### **3. Select Environment**
1. In the top-right corner, click the environment dropdown
2. Select **"Dry Cleaning API Environment"**

## 🎯 **Collection Structure**

### **🔐 Authentication (8 endpoints)**
- **Register User** - Create new account
- **Login User** - Get authentication token
- **Logout User** - Invalidate token
- **Get User Profile** - View profile
- **Update User Profile** - Edit profile
- **Change Password** - Update password
- **Request Password Reset** - Reset password
- **Get User Dashboard** - Dashboard data

### **🛠️ Services (7 endpoints)**
- **Get Service Categories** - List categories
- **Get All Services** - List services
- **Get Service Details** - Service info
- **Get Service Estimate** - Price estimate
- **Bulk Service Estimate** - Multiple services
- **Search Services** - Search by keyword
- **Get Popular Services** - Popular items

### **📦 Orders (7 endpoints)**
- **Get User Orders** - List orders
- **Create New Order** - Place order
- **Get Order Details** - Order info
- **Update Order Status** - Change status
- **Track Order** - Order tracking
- **Cancel Order** - Cancel order
- **Get Order History** - Order history

### **💳 Payments (8 endpoints)**
- **Get User Payments** - List payments
- **Create Payment** - New payment
- **Get Payment Details** - Payment info
- **Create Stripe Payment Intent** - Stripe integration
- **Create Razorpay Order** - Razorpay integration
- **Verify Payment** - Payment verification
- **Get Refunds** - List refunds
- **Create Refund** - Process refund

### **🔔 Notifications (6 endpoints)**
- **Get User Notifications** - List notifications
- **Get Notification Details** - Notification info
- **Mark Notification as Read** - Mark as read
- **Get Notification Preferences** - User preferences
- **Update Notification Preferences** - Update preferences
- **Get Notification Stats** - Statistics

### **📊 System (3 endpoints)**
- **API Root** - API information
- **Health Check** - System health
- **API Overview** - Complete endpoint list

## 🔑 **Authentication Flow**

### **Step 1: Register a User**
1. Go to **"🔐 Authentication"** folder
2. Run **"Register User"** request
3. Note the response for user details

### **Step 2: Login to Get Token**
1. Run **"Login User"** request
2. The token will be automatically saved to `{{auth_token}}`
3. Check the **"Tests"** tab to see the token saving logic

### **Step 3: Use Protected Endpoints**
- All subsequent requests will use the saved token
- Token is automatically included in Authorization header

## 🎯 **Quick Start Workflow**

### **1. Test System Endpoints**
```
1. API Root → Get API information
2. Health Check → Verify server status
3. API Overview → See all endpoints
```

### **2. Test Public Endpoints**
```
1. Get Service Categories → View available services
2. Get All Services → Browse services
3. Get Service Estimate → Test pricing
```

### **3. Test Authentication**
```
1. Register User → Create account
2. Login User → Get token
3. Get User Profile → Verify authentication
```

### **4. Test Full Order Flow**
```
1. Create New Order → Place order
2. Get Order Details → View order
3. Update Order Status → Change status
4. Track Order → Monitor progress
```

## 🔧 **Environment Variables**

| Variable | Description | Example |
|----------|-------------|---------|
| `{{base_url}}` | API base URL | `http://localhost:8000` |
| `{{auth_token}}` | Authentication token | `Token abc123...` |
| `{{user_id}}` | Current user ID | `1` |
| `{{order_id}}` | Order ID for testing | `1` |
| `{{payment_id}}` | Payment ID for testing | `1` |
| `{{service_id}}` | Service ID for testing | `1` |
| `{{notification_id}}` | Notification ID for testing | `1` |

## 📝 **Example Requests**

### **Register User**
```json
{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password2": "testpass123",
    "first_name": "Test",
    "last_name": "User",
    "phone": "+1234567890",
    "address": "123 Test Street",
    "city": "Test City",
    "state": "Test State",
    "zip_code": "12345"
}
```

### **Create Order**
```json
{
    "pickup_address": "123 Pickup Street",
    "pickup_city": "Pickup City",
    "pickup_state": "Pickup State",
    "pickup_zip_code": "12345",
    "pickup_phone": "+1234567890",
    "pickup_date": "2024-01-15",
    "pickup_time": "10:00:00",
    "delivery_address": "456 Delivery Street",
    "delivery_city": "Delivery City",
    "delivery_state": "Delivery State",
    "delivery_zip_code": "54321",
    "delivery_phone": "+1234567890",
    "delivery_date": "2024-01-17",
    "delivery_time": "14:00:00",
    "special_instructions": "Handle with care",
    "items": [
        {
            "service_id": 1,
            "quantity": 2,
            "urgency": "normal",
            "special_instructions": "Gentle wash"
        }
    ]
}
```

## 🚨 **Important Notes**

### **Authentication**
- Most endpoints require authentication
- Use **"Login User"** to get a token
- Token is automatically saved and used
- Token expires after logout

### **Error Handling**
- Check response status codes
- Review error messages in response body
- Common errors: 401 (Unauthorized), 400 (Bad Request), 404 (Not Found)

### **Testing Order**
1. **Start with public endpoints** (no auth required)
2. **Register and login** to get token
3. **Test protected endpoints** with token
4. **Use realistic data** for better testing

## 🔄 **Automation Features**

### **Token Auto-Save**
The **"Login User"** request automatically saves the token to `{{auth_token}}` variable.

### **Variable Usage**
All requests use environment variables for dynamic values:
- `{{base_url}}` for API URL
- `{{auth_token}}` for authentication
- `{{order_id}}`, `{{payment_id}}` for testing

## 📊 **Testing Scenarios**

### **Scenario 1: New User Journey**
1. Register → Login → Browse Services → Create Order → Make Payment

### **Scenario 2: Existing User**
1. Login → View Orders → Track Order → Update Profile

### **Scenario 3: Admin Operations**
1. Login → View All Orders → Update Status → Send Notifications

## 🎉 **Ready to Test!**

Your Postman collection is now ready to use! Start with the system endpoints to verify your API is running, then proceed with the authentication flow to test all features.

**Happy Testing! 🚀** 