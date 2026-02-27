from django.contrib import admin
from .models import (
    Internship, Application, Job, JobApplication, JobBookmark, JobView,
    Interview, StatusChange, RejectionTag, AcceptanceTag, ApplicationRemark,
    AutoScreeningResult, CandidateFeedback,
)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'job_type', 'experience_level', 'is_remote', 'is_premium', 'auto_screen_enabled', 'status', 'application_count', 'created_at')
    list_filter = ('job_type', 'experience_level', 'is_remote', 'is_premium', 'auto_screen_enabled', 'status')
    search_fields = ('title', 'company__username', 'required_skills', 'location')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'job', 'email', 'status', 'match_score', 'auto_status', 'years_of_experience', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('full_name', 'email', 'job__title')
    readonly_fields = ('applied_at', 'updated_at')
    ordering = ('-applied_at',)


@admin.register(JobBookmark)
class JobBookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'job__title')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(JobView)
class JobViewAdmin(admin.ModelAdmin):
    list_display = ('job', 'viewer', 'ip_address', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('job__title', 'viewer__username', 'ip_address')
    readonly_fields = ('viewed_at',)
    ordering = ('-viewed_at',)


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('application', 'interview_type', 'scheduled_at', 'duration_minutes', 'status')
    list_filter = ('interview_type', 'status', 'scheduled_at')
    search_fields = ('application__full_name', 'application__job__title')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'internship_type', 'is_premium', 'location', 'status', 'application_count', 'created_at')
    list_filter = ('internship_type', 'is_premium', 'status', 'created_at')
    search_fields = ('title', 'company__username', 'required_skills', 'location')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Info', {'fields': ('company', 'title', 'description', 'internship_type', 'status')}),
        ('Requirements', {'fields': ('required_skills', 'qualifications', 'experience')}),
        ('Location & Contact', {'fields': ('location', 'email')}),
        ('Additional', {'fields': ('salary', 'duration')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'internship', 'email', 'status', 'match_score', 'auto_status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('full_name', 'email', 'internship__title')
    readonly_fields = ('applied_at', 'updated_at')
    ordering = ('-applied_at',)
    
    fieldsets = (
        ('Application', {'fields': ('internship', 'applicant', 'status')}),
        ('Personal Details', {'fields': ('full_name', 'email', 'phone')}),
        ('Documents', {'fields': ('cv', 'cover_letter')}),
        ('Links', {'fields': ('linkedin', 'portfolio')}),
        ('Timestamps', {'fields': ('applied_at', 'updated_at')}),
    )


@admin.register(StatusChange)
class StatusChangeAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'old_status', 'new_status', 'changed_by')
    list_filter = ('new_status', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(RejectionTag)
class RejectionTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'sort_order')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(AcceptanceTag)
class AcceptanceTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'sort_order')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class ApplicationRemarkInline(admin.TabularInline):
    model = ApplicationRemark
    extra = 0
    readonly_fields = ('created_at', 'created_by')
    fk_name = 'job_application'


@admin.register(ApplicationRemark)
class ApplicationRemarkAdmin(admin.ModelAdmin):
    list_display = ('remark_type', 'job_application', 'internship_application', 'created_by', 'created_at')
    list_filter = ('remark_type', 'created_at')
    search_fields = ('custom_remarks', 'hr_notes')
    readonly_fields = ('created_at',)
    filter_horizontal = ('rejection_tags', 'acceptance_tags')


@admin.register(AutoScreeningResult)
class AutoScreeningResultAdmin(admin.ModelAdmin):
    list_display = ('job_application', 'internship_application', 'total_score', 'suggested_status', 'screened_at')
    list_filter = ('suggested_status', 'screened_at')
    readonly_fields = ('screened_at',)


@admin.register(CandidateFeedback)
class CandidateFeedbackAdmin(admin.ModelAdmin):
    list_display = ('job_application', 'internship_application', 'feedback_type', 'is_visible', 'created_by', 'created_at')
    list_filter = ('feedback_type', 'is_visible', 'created_at')
    search_fields = ('message', 'suggested_skills')
    readonly_fields = ('created_at',)
