from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json

def home(request):
    """Home page with hero section and featured services"""
    return render(request, 'frontend/home.html')

def services(request):
    """Services page showing all available services"""
    return render(request, 'frontend/services.html')

def pricing(request):
    """Pricing page with service rates"""
    return render(request, 'frontend/pricing.html')

def contact(request):
    """Contact page with contact form"""
    return render(request, 'frontend/contact.html')

@login_required
def dashboard(request):
    """User dashboard with order summary and quick actions"""
    return render(request, 'frontend/dashboard.html')

@login_required
def profile(request):
    """User profile management"""
    return render(request, 'frontend/profile.html')

@login_required
def orders(request):
    """User orders page"""
    return render(request, 'frontend/orders.html')

@login_required
def order_detail(request, order_id):
    """Order detail page"""
    return render(request, 'frontend/order_detail.html', {'order_id': order_id})

@login_required
def create_order(request):
    """Create new order page"""
    return render(request, 'frontend/create_order.html')

@login_required
def notifications(request):
    """User notifications page"""
    return render(request, 'frontend/notifications.html')

def login_view(request):
    """Login page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'redirect': '/dashboard/'})
                return redirect('dashboard')
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Invalid credentials'}, status=400)
                messages.error(request, 'Invalid username or password.')
    
    return render(request, 'frontend/login.html')

def register_view(request):
    """Registration page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        from django.contrib.auth.models import User
        from accounts.models import UserProfile
        
        try:
            # Create user
            user = User.objects.create_user(
                username=request.POST.get('username'),
                email=request.POST.get('email'),
                password=request.POST.get('password'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name')
            )
            
            # Update user profile (created by signal)
            user.userprofile.phone_number = request.POST.get('phone')
            user.userprofile.address = request.POST.get('address')
            user.userprofile.city = request.POST.get('city')
            user.userprofile.state = request.POST.get('state')
            user.userprofile.pincode = request.POST.get('zip_code')
            user.userprofile.save()
            
            messages.success(request, 'Account created successfully! Please sign in.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
    
    return render(request, 'frontend/register.html')

def logout_view(request):
    """Logout view"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

# API proxy views for AJAX calls
@csrf_exempt
def api_proxy(request, endpoint):
    """Proxy for API calls from frontend"""
    api_base_url = 'http://localhost:8000/api/'
    
    try:
        if request.method == 'GET':
            response = requests.get(f"{api_base_url}{endpoint}/", headers=request.headers)
        elif request.method == 'POST':
            response = requests.post(f"{api_base_url}{endpoint}/", json=request.POST, headers=request.headers)
        elif request.method == 'PUT':
            response = requests.put(f"{api_base_url}{endpoint}/", json=request.POST, headers=request.headers)
        elif request.method == 'DELETE':
            response = requests.delete(f"{api_base_url}{endpoint}/", headers=request.headers)
        
        # Check if response has content and is JSON
        if response.content and response.headers.get('content-type', '').startswith('application/json'):
            try:
                return JsonResponse(response.json(), status=response.status_code)
            except ValueError:
                # If JSON parsing fails, return the raw content
                return JsonResponse({'error': 'Invalid JSON response'}, status=500)
        else:
            # Return empty response for non-JSON content
            return JsonResponse({'error': 'No content'}, status=response.status_code)
            
    except requests.RequestException as e:
        return JsonResponse({'error': f'Request failed: {str(e)}'}, status=500)
    except Exception as e:
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500) 