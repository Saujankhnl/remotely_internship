from django.contrib import admin
from .models import Internship, Application, Job, JobApplication, JobBookmark, JobView, Interview


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'job_type', 'experience_level', 'is_remote', 'status', 'application_count', 'created_at')
    list_filter = ('job_type', 'experience_level', 'is_remote', 'status')
    search_fields = ('title', 'company__username', 'required_skills', 'location')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'job', 'email', 'status', 'years_of_experience', 'applied_at')
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
    list_display = ('title', 'company', 'internship_type', 'location', 'status', 'application_count', 'created_at')
    list_filter = ('internship_type', 'status', 'created_at')
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
    list_display = ('full_name', 'internship', 'email', 'status', 'applied_at')
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
