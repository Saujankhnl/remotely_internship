from django.contrib import admin
from .models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'application', 'created_at')
    list_filter = ('created_at',)
    search_fields = (
        'application__full_name',
        'application__job__title',
        'application__applicant__username',
    )
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'sender', 'short_content', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('content', 'sender__username', 'room__application__job__title')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    @admin.display(description='Content')
    def short_content(self, obj):
        return obj.content[:80]
