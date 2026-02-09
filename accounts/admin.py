from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import (
    CustomUser, UserProfile, CompanyProfile, PasswordResetOTP,
    UserExperience, UserEducation, UserProject,
)


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


class UserExperienceInline(admin.TabularInline):
    model = UserExperience
    extra = 0
    fields = ('title', 'company_name', 'employment_type', 'start_date', 'end_date', 'is_current', 'sort_order')


class UserEducationInline(admin.TabularInline):
    model = UserEducation
    extra = 0
    fields = ('school', 'degree', 'field_of_study', 'start_year', 'end_year', 'sort_order')


class UserProjectInline(admin.TabularInline):
    model = UserProject
    extra = 0
    fields = ('name', 'url', 'technologies', 'is_featured', 'sort_order')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'headline', 'phone', 'location', 'completeness_score', 'is_public', 'open_to_work', 'created_at')
    list_filter = ('is_public', 'open_to_work', 'created_at')
    search_fields = ('user__username', 'user__email', 'full_name', 'skills', 'headline')
    readonly_fields = ('created_at', 'updated_at', 'completeness_score')
    inlines = [UserExperienceInline, UserEducationInline, UserProjectInline]
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Public Profile', {'fields': ('is_public', 'headline', 'open_to_work', 'completeness_score')}),
        ('Personal Info', {'fields': ('full_name', 'phone', 'location', 'bio', 'profile_photo')}),
        ('Professional', {'fields': ('skills', 'education', 'experience', 'resume')}),
        ('Social Links', {'fields': ('linkedin', 'github', 'facebook', 'instagram', 'whatsapp')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'industry', 'location', 'approval_status', 'is_verified', 'completeness_score', 'created_at')
    list_filter = ('approval_status', 'is_verified', 'industry', 'company_size', 'created_at')
    search_fields = ('user__username', 'user__email', 'company_name', 'industry', 'slug')
    readonly_fields = ('created_at', 'updated_at', 'completeness_score', 'approved_at', 'verified_at')
    prepopulated_fields = {'slug': ('company_name',)}
    actions = ['approve_companies', 'reject_companies', 'suspend_companies']
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Company Info', {'fields': ('company_name', 'slug', 'phone', 'location', 'bio', 'logo')}),
        ('Business Details', {'fields': ('industry', 'company_size', 'founded_year')}),
        ('Public Profile', {'fields': ('is_public', 'completeness_score')}),
        ('Approval Workflow', {
            'fields': ('approval_status', 'approved_at', 'approved_by', 'rejection_reason'),
            'classes': ('wide',),
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_at'),
        }),
        ('Online Presence', {'fields': ('website', 'linkedin', 'facebook', 'instagram', 'whatsapp')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    @admin.action(description="Approve selected companies")
    def approve_companies(self, request, queryset):
        updated = queryset.update(
            approval_status='approved',
            approved_at=timezone.now(),
            approved_by=request.user,
            rejection_reason='',
        )
        self.message_user(request, f"{updated} company/companies approved successfully.")

    @admin.action(description="Reject selected companies")
    def reject_companies(self, request, queryset):
        updated = queryset.update(
            approval_status='rejected',
            rejection_reason='Your company profile does not meet our requirements. Please update your profile and try again.',
        )
        self.message_user(request, f"{updated} company/companies rejected.")

    @admin.action(description="Suspend selected companies")
    def suspend_companies(self, request, queryset):
        from internships.models import Job, Internship
        company_users = queryset.values_list('user', flat=True)
        Job.objects.filter(company__in=company_users, status='open').update(status='closed')
        Internship.objects.filter(company__in=company_users, status='open').update(status='closed')
        updated = queryset.update(approval_status='suspended')
        self.message_user(request, f"{updated} company/companies suspended. All their open posts have been closed.")


@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('otp_hash', 'created_at')
