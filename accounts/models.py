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
    
    # Public profile controls
    is_public = models.BooleanField(default=True)
    headline = models.CharField(max_length=160, blank=True, help_text="e.g., CS Student | Frontend Developer")
    open_to_work = models.BooleanField(default=False)
    
    # Trust
    completeness_score = models.PositiveSmallIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_completeness(self):
        score = 0
        if self.full_name: score += 10
        if self.profile_photo: score += 10
        if self.bio and len(self.bio) >= 50: score += 10
        if self.skills: score += 10
        if self.education: score += 10
        if self.experience: score += 10
        if self.resume: score += 10
        if self.location: score += 10
        if any([self.linkedin, self.github, self.facebook, self.instagram]): score += 10
        if self.headline: score += 10
        self.completeness_score = score
        return score

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
    
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    
    # Public profile controls
    is_public = models.BooleanField(default=True)
    
    # Approval workflow
    APPROVAL_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    )
    approval_status = models.CharField(
        max_length=10, choices=APPROVAL_STATUS_CHOICES, default='pending'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        CustomUser,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_companies'
    )
    rejection_reason = models.TextField(blank=True)
    
    # Verification badge
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Trust
    completeness_score = models.PositiveSmallIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_completeness(self):
        score = 0
        if self.company_name: score += 10
        if self.logo: score += 10
        if self.bio and len(self.bio) >= 80: score += 10
        if self.industry: score += 10
        if self.company_size: score += 10
        if self.location: score += 10
        if self.phone: score += 10
        if self.website: score += 10
        if self.founded_year: score += 10
        if any([self.linkedin, self.facebook, self.instagram]): score += 10
        self.completeness_score = score
        return score

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.company_name or self.user.username)
            slug = base_slug
            counter = 2
            while CompanyProfile.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

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


class UserExperience(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='experiences')
    title = models.CharField(max_length=120)
    company_name = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=120, blank=True)
    EMPLOYMENT_TYPE_CHOICES = (
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
        ('volunteer', 'Volunteer'),
    )
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', '-start_date', '-created_at']
        verbose_name = "User Experience"
        verbose_name_plural = "User Experiences"

    def __str__(self):
        return f"{self.title} at {self.company_name}"


class UserEducation(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='educations')
    school = models.CharField(max_length=160)
    degree = models.CharField(max_length=120, blank=True)
    field_of_study = models.CharField(max_length=120, blank=True)
    start_year = models.PositiveIntegerField(null=True, blank=True)
    end_year = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', '-end_year', '-start_year', '-created_at']
        verbose_name = "User Education"
        verbose_name_plural = "User Education"

    def __str__(self):
        return f"{self.degree} - {self.school}"


class UserProject(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=160)
    url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    technologies = models.CharField(max_length=250, blank=True, help_text="Comma separated")
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', '-is_featured', '-created_at']
        verbose_name = "User Project"
        verbose_name_plural = "User Projects"

    def __str__(self):
        return self.name
