from django.db import models
from django.conf import settings


class GeneratedResume(models.Model):
    TEMPLATE_CHOICES = (
        ('professional', 'Professional'),
        ('modern', 'Modern'),
        ('minimal', 'Minimal'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generated_resumes'
    )
    template_name = models.CharField(max_length=50, choices=TEMPLATE_CHOICES)
    file = models.FileField(upload_to='generated_resumes/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Generated Resume"
        verbose_name_plural = "Generated Resumes"

    def __str__(self):
        return f"{self.user.username} - {self.get_template_name_display()} - {self.created_at.strftime('%Y-%m-%d')}"
