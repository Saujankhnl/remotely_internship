from django.contrib import admin
from .models import GeneratedResume


@admin.register(GeneratedResume)
class GeneratedResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'template_name', 'created_at')
    list_filter = ('template_name', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)
