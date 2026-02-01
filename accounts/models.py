from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import hashlib


class CustomUser(AbstractUser):
    """Base authentication model - stores email and password"""
    USER_TYPE_CHOICES = (
        ('user', 'User'),
        ('company', 'Company'),
    )
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = "User Account"
        verbose_name_plural = "User Accounts"


class UserProfile(models.Model):
    """Profile for Users (Job Seekers) - Separate table"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_profile')
    
    # Personal Info
    full_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    
    # Professional Info
    skills = models.CharField(max_length=500, blank=True, help_text="Comma separated skills")
    education = models.CharField(max_length=200, blank=True)
    experience = models.TextField(blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    
    # Social Links
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - User Profile"
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class CompanyProfile(models.Model):
    """Profile for Companies - Separate table"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='company_profile')
    
    # Company Info
    company_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True, help_text="Company description")
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    
    # Business Info
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=50, blank=True, help_text="e.g., 1-10, 11-50, 51-200")
    founded_year = models.PositiveIntegerField(blank=True, null=True)
    
    # Social & Contact
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name or self.user.username} - Company Profile"
    
    class Meta:
        verbose_name = "Company Profile"
        verbose_name_plural = "Company Profiles"


class PasswordResetOTP(models.Model):
    """OTP for password reset - stored in hashed form"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    @staticmethod
    def hash_otp(otp):
        return hashlib.sha256(str(otp).encode()).hexdigest()

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def verify_otp(self, otp):
        return self.otp_hash == self.hash_otp(otp) and self.is_valid()

    @classmethod
    def create_otp(cls, user, otp):
        cls.objects.filter(user=user, is_used=False).delete()
        return cls.objects.create(
            user=user,
            otp_hash=cls.hash_otp(otp),
            expires_at=timezone.now() + timedelta(minutes=5)
        )

    class Meta:
        verbose_name = "Password Reset OTP"
        verbose_name_plural = "Password Reset OTPs"
