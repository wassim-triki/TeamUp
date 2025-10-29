from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, EmailVerificationToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin configuration."""
    list_display = ('email', 'username', 'is_active', 'email_verified_at', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('email_verified_at', 'last_login', 'date_joined')}),
    )
    
    readonly_fields = ('date_joined', 'last_login')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """UserProfile admin configuration."""
    list_display = ('user', 'full_name', 'gender', 'country', 'city', 'created_at')
    search_fields = ('user__email', 'first_name', 'last_name', 'city', 'country')
    list_filter = ('created_at', 'gender', 'country')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Required Info', {'fields': ('first_name', 'last_name', 'gender', 'country')}),
        ('Optional Info', {'fields': ('avatar', 'date_of_birth', 'age', 'city', 'phone', 'bio')}),
        ('Sports & Availability', {'fields': ('sports', 'availability')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """EmailVerificationToken admin configuration."""
    list_display = ('user', 'token_short', 'created_at', 'expires_at', 'used', 'is_valid_status')
    list_filter = ('used', 'created_at', 'expires_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('token', 'created_at')
    
    def token_short(self, obj):
        """Display shortened token for readability."""
        return f"{str(obj.token)[:20]}..."
    token_short.short_description = 'Token'
    
    def is_valid_status(self, obj):
        """Display validation status."""
        return obj.is_valid()
    is_valid_status.boolean = True
    is_valid_status.short_description = 'Valid'
