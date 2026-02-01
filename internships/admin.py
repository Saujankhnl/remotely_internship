from django.contrib import admin
from .models import Internship, Application


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
