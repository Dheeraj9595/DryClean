from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('reset-password/', views.ResetPasswordEmailView.as_view(), name='reset_password'),
    path('reset-password/confirm/', views.ResetPasswordConfirmView.as_view(), name='reset_password_confirm'),
    
    # User Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update-picture/', views.update_profile_picture, name='update_profile_picture'),
    path('user/', views.UserDetailView.as_view(), name='user_detail'),
    
    # Dashboard
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('status/', views.check_auth_status, name='auth_status'),
] 