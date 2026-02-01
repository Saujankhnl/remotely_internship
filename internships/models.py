from django.db import models
from django.conf import settings


class Internship(models.Model):
    """Internship posting model - only companies can create"""
    TYPE_CHOICES = (
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    )
    
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
    )
    
    company = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='internships'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    internship_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    
    # Requirements
    required_skills = models.CharField(max_length=500, help_text="Comma separated skills")
    qualifications = models.TextField()
    experience = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Required for paid internships"
    )
    
    # Location & Contact
    location = models.CharField(max_length=200)
    email = models.EmailField()
    
    # Optional fields
    salary = models.CharField(max_length=100, blank=True, help_text="For paid internships")
    duration = models.CharField(max_length=100, blank=True, help_text="e.g., 3 months, 6 months")
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Internship"
        verbose_name_plural = "Internships"
    
    def __str__(self):
        return f"{self.title} at {self.company.username}"
    
    @property
    def application_count(self):
        return self.applications.count()
    
    def get_skills_list(self):
        return [skill.strip() for skill in self.required_skills.split(',') if skill.strip()]


class Application(models.Model):
    """Application model - users apply to internships"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
    )
    
    internship = models.ForeignKey(
        Internship, 
        on_delete=models.CASCADE, 
        related_name='applications'
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='applications'
    )
    
    # Personal details
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Application content
    cover_letter = models.TextField(blank=True)
    cv = models.FileField(upload_to='cvs/')
    
    # Additional info
    linkedin = models.URLField(blank=True)
    portfolio = models.URLField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-applied_at']
        verbose_name = "Application"
        verbose_name_plural = "Applications"
        constraints = [
            models.UniqueConstraint(
                fields=['internship', 'applicant'],
                name='unique_application_per_internship'
            )
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.internship.title}"
