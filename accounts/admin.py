from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile, CompanyProfile, PasswordResetOTP


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('user_type',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('User Type', {'fields': ('user_type',)}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'location', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'full_name', 'skills')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Personal Info', {'fields': ('full_name', 'phone', 'location', 'bio', 'profile_photo')}),
        ('Professional', {'fields': ('skills', 'education', 'experience', 'resume')}),
        ('Social Links', {'fields': ('linkedin', 'github', 'facebook', 'instagram', 'whatsapp')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'industry', 'location', 'created_at')
    list_filter = ('industry', 'company_size', 'created_at')
    search_fields = ('user__username', 'user__email', 'company_name', 'industry')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Company Info', {'fields': ('company_name', 'phone', 'location', 'bio', 'logo')}),
        ('Business Details', {'fields': ('industry', 'company_size', 'founded_year')}),
        ('Online Presence', {'fields': ('website', 'linkedin', 'facebook', 'instagram', 'whatsapp')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('otp_hash', 'created_at')
