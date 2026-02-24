from django.db import models
from django.conf import settings


class ChatRoom(models.Model):
    """Private chat room linked to a job application"""
    application = models.OneToOneField(
        'internships.JobApplication',
        on_delete=models.CASCADE,
        related_name='chat_room',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Chat Room"
        verbose_name_plural = "Chat Rooms"

    def __str__(self):
        return f"Chat: {self.application.full_name} – {self.application.job.title}"

    def get_participants(self):
        return [self.application.applicant, self.application.job.company]

    @property
    def job_title(self):
        return self.application.job.title

    @property
    def applicant_name(self):
        return self.application.full_name

    @property
    def company_name(self):
        profile = getattr(self.application.job.company, 'company_profile', None)
        if profile and profile.company_name:
            return profile.company_name
        return self.application.job.company.username


class Message(models.Model):
    """Individual message within a chat room"""
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_messages',
    )
    content = models.TextField()
    attachment = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
