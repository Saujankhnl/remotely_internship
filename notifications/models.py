from django.db import models
from django.conf import settings


class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = (
        ('application_status', 'Application Status'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('profile_viewed', 'Profile Viewed'),
        ('job_match', 'Job Match'),
        ('new_application', 'New Application'),
        ('general', 'General'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    message = models.CharField(max_length=500)
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='general',
    )
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_url = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"{self.user.username} - {self.message[:50]}"

    @classmethod
    def create_notification(cls, user, message, notification_type='general',
                            related_object_id=None, related_url=''):
        return cls.objects.create(
            user=user,
            message=message,
            notification_type=notification_type,
            related_object_id=related_object_id,
            related_url=related_url,
        )
