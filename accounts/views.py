from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import UserProfile
from .serializers import (
    UserSerializer, UserProfileSerializer, RegisterSerializer,
    ChangePasswordSerializer, ResetPasswordEmailSerializer, ResetPasswordConfirmSerializer
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })


class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Error logging out.'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user.userprofile


class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Delete the old token and create a new one
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        
        return Response({
            'message': 'Password changed successfully.',
            'token': token.key
        }, status=status.HTTP_200_OK)


class ResetPasswordEmailView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordEmailSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Generate password reset token
        token = Token.objects.get_or_create(user=user)[0]
        
        # In a real application, you would send an email with the reset link
        # For now, we'll just return the token
        return Response({
            'message': 'Password reset email sent.',
            'token': token.key
        }, status=status.HTTP_200_OK)


class ResetPasswordConfirmView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordConfirmSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # In a real application, you would validate the token and uidb64
        # For now, we'll just update the password
        try:
            user = User.objects.get(id=request.data.get('uidb64'))
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Delete the old token and create a new one
            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)
            
            return Response({
                'message': 'Password reset successfully.',
                'token': token.key
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid user.'
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard(request):
    """Get user dashboard data"""
    user = request.user
    profile = user.userprofile
    
    # Get user's recent orders
    recent_orders = user.orders.order_by('-created_at')[:5]
    
    # Get user's notifications
    recent_notifications = user.notifications.filter(is_read=False).order_by('-created_at')[:5]
    
    dashboard_data = {
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined,
        },
        'profile': {
            'phone_number': profile.phone_number,
            'address': profile.address,
            'city': profile.city,
            'state': profile.state,
            'pincode': profile.pincode,
        },
        'stats': {
            'total_orders': user.orders.count(),
            'pending_orders': user.orders.filter(status='pending').count(),
            'completed_orders': user.orders.filter(status='delivered').count(),
            'unread_notifications': user.notifications.filter(is_read=False).count(),
        },
        'recent_orders': [
            {
                'id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'total_amount': order.total_amount,
                'created_at': order.created_at,
            }
            for order in recent_orders
        ],
        'recent_notifications': [
            {
                'id': notification.id,
                'title': notification.title,
                'notification_type': notification.notification_type,
                'created_at': notification.created_at,
            }
            for notification in recent_notifications
        ]
    }
    
    return Response(dashboard_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_profile_picture(request):
    """Update user profile picture"""
    if 'profile_picture' not in request.FILES:
        return Response({
            'error': 'Profile picture is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    profile = request.user.userprofile
    profile.profile_picture = request.FILES['profile_picture']
    profile.save()
    
    return Response({
        'message': 'Profile picture updated successfully.',
        'profile_picture_url': profile.profile_picture.url if profile.profile_picture else None
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_auth_status(request):
    """Check if user is authenticated and return user info"""
    user = request.user
    return Response({
        'is_authenticated': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    })
