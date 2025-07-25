from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone_number', 'get_city')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'userprofile__phone_number', 'userprofile__city')
    
    def get_phone_number(self, obj):
        return obj.userprofile.phone_number if hasattr(obj, 'userprofile') else '-'
    get_phone_number.short_description = 'Phone Number'
    
    def get_city(self, obj):
        return obj.userprofile.city if hasattr(obj, 'userprofile') else '-'
    get_city.short_description = 'City'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'city', 'state', 'pincode', 'created_at')
    list_filter = ('city', 'state', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number', 'address', 'city')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone_number')
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'state', 'pincode')
        }),
        ('Profile', {
            'fields': ('profile_picture',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
