from django.db import models
from django.conf import settings


class Job(models.Model):
    """Job posting model - only companies can create"""
    JOB_TYPE_CHOICES = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('remote', 'Remote'),
    )
    
    EXPERIENCE_CHOICES = (
        ('fresher', 'Fresher (0-1 years)'),
        ('junior', 'Junior (1-3 years)'),
        ('mid', 'Mid-Level (3-5 years)'),
        ('senior', 'Senior (5-8 years)'),
        ('lead', 'Lead (8+ years)'),
    )
    
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
    )
    
    company = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='jobs'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    
    # Requirements
    required_skills = models.CharField(max_length=500, help_text="Comma separated skills")
    qualifications = models.TextField()
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    
    # Salary
    salary_min = models.PositiveIntegerField(blank=True, null=True, help_text="Minimum salary")
    salary_max = models.PositiveIntegerField(blank=True, null=True, help_text="Maximum salary")
    salary_currency = models.CharField(max_length=10, default='USD')
    
    # Location & Contact
    location = models.CharField(max_length=200)
    is_remote = models.BooleanField(default=False)
    email = models.EmailField()
    
    # Additional
    benefits = models.TextField(blank=True, help_text="Benefits offered")
    deadline = models.DateField(blank=True, null=True)
    
    # Premium & Screening
    is_premium = models.BooleanField(default=False, help_text="Premium listing with higher visibility")
    auto_screen_enabled = models.BooleanField(default=False, help_text="Enable automatic applicant screening")
    required_course = models.CharField(max_length=200, blank=True, help_text="Preferred course/degree e.g., Computer Science")
    min_gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, help_text="Minimum GPA requirement")
    ENGLISH_LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('fluent', 'Fluent'),
        ('native', 'Native'),
    )
    preferred_english_level = models.CharField(max_length=20, choices=ENGLISH_LEVEL_CHOICES, blank=True)
    preferred_internet_quality = models.CharField(max_length=20, blank=True, help_text="Minimum internet quality: poor/average/good/excellent")
    preferred_location = models.CharField(max_length=200, blank=True, help_text="Preferred candidate location")
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_premium', '-created_at']
        verbose_name = "Job"
        verbose_name_plural = "Jobs"
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['company', 'status']),
            models.Index(fields=['-is_premium', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} at {self.company.username}"
    
    @property
    def application_count(self):
        return self.job_applications.count()
    
    def get_skills_list(self):
        return [skill.strip() for skill in self.required_skills.split(',') if skill.strip()]
    
    def get_salary_display(self):
        if self.salary_min and self.salary_max:
            return f"{self.salary_currency} {self.salary_min:,} - {self.salary_max:,}"
        elif self.salary_min:
            return f"{self.salary_currency} {self.salary_min:,}+"
        elif self.salary_max:
            return f"Up to {self.salary_currency} {self.salary_max:,}"
        return "Not disclosed"


class JobApplication(models.Model):
    """Job Application model"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('on_hold', 'On Hold'),
        ('interview', 'Interview Scheduled'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
    )
    
    job = models.ForeignKey(
        Job, 
        on_delete=models.CASCADE, 
        related_name='job_applications'
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='job_applications'
    )
    
    # Personal details
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Application content
    cover_letter = models.TextField(blank=True)
    cv = models.FileField(upload_to='job_cvs/')
    expected_salary = models.PositiveIntegerField(blank=True, null=True)
    
    # Additional info
    linkedin = models.URLField(blank=True)
    portfolio = models.URLField(blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    notice_period = models.CharField(max_length=50, blank=True, help_text="e.g., 2 weeks, 1 month")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    match_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Auto-screening match score 0-100")
    auto_status = models.CharField(max_length=20, blank=True, help_text="Auto-screening suggested status")
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-applied_at']
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"
        constraints = [
            models.UniqueConstraint(
                fields=['job', 'applicant'],
                name='unique_job_application'
            )
        ]
        indexes = [
            models.Index(fields=['applicant', 'status']),
            models.Index(fields=['job', 'status']),
            models.Index(fields=['applied_at']),
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.job.title}"


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
    deadline = models.DateField(blank=True, null=True)
    
    # Premium & Screening
    is_premium = models.BooleanField(default=False, help_text="Premium listing with higher visibility")
    auto_screen_enabled = models.BooleanField(default=False, help_text="Enable automatic applicant screening")
    required_course = models.CharField(max_length=200, blank=True, help_text="Preferred course/degree")
    min_gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    ENGLISH_LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('fluent', 'Fluent'),
        ('native', 'Native'),
    )
    preferred_english_level = models.CharField(max_length=20, choices=ENGLISH_LEVEL_CHOICES, blank=True)
    preferred_internet_quality = models.CharField(max_length=20, blank=True)
    preferred_location = models.CharField(max_length=200, blank=True)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_premium', '-created_at']
        verbose_name = "Internship"
        verbose_name_plural = "Internships"
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['company', 'status']),
        ]
    
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
        ('on_hold', 'On Hold'),
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
    match_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Auto-screening match score 0-100")
    auto_status = models.CharField(max_length=20, blank=True, help_text="Auto-screening suggested status")
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
        indexes = [
            models.Index(fields=['applicant', 'status']),
            models.Index(fields=['internship', 'status']),
            models.Index(fields=['applied_at']),
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.internship.title}"


class JobBookmark(models.Model):
    """Bookmark model - users can save/bookmark jobs"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_bookmarks'
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Job Bookmark"
        verbose_name_plural = "Job Bookmarks"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'job'],
                name='unique_job_bookmark'
            )
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.job.title}"


class JobView(models.Model):
    """Track job views for analytics"""
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='views'
    )
    viewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_views',
        null=True,
        blank=True
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-viewed_at']
        verbose_name = "Job View"
        verbose_name_plural = "Job Views"
    
    def __str__(self):
        viewer_name = self.viewer.username if self.viewer else 'Anonymous'
        return f"{viewer_name} viewed {self.job.title}"


class Interview(models.Model):
    """Interview scheduling model"""
    INTERVIEW_TYPE_CHOICES = (
        ('phone', 'Phone'),
        ('video', 'Video Call'),
        ('onsite', 'On-site'),
        ('technical', 'Technical'),
    )
    
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    )
    
    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name='interviews'
    )
    scheduled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='scheduled_interviews'
    )
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPE_CHOICES)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    location = models.CharField(max_length=500, blank=True, help_text="For onsite or meeting link")
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_at']
        verbose_name = "Interview"
        verbose_name_plural = "Interviews"
        indexes = [
            models.Index(fields=['status', 'scheduled_at']),
        ]
    
    def __str__(self):
        return f"Interview for {self.application.full_name} - {self.get_interview_type_display()}"


class StatusChange(models.Model):
    """Tracks status changes for applications (audit trail / timeline)."""
    job_application = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE,
        related_name='status_history', null=True, blank=True,
    )
    internship_application = models.ForeignKey(
        Application, on_delete=models.CASCADE,
        related_name='status_history', null=True, blank=True,
    )
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Status Change"
        verbose_name_plural = "Status Changes"

    def __str__(self):
        return f"{self.old_status} → {self.new_status} at {self.created_at}"


class RejectionTag(models.Model):
    """Predefined rejection reasons"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.CharField(max_length=300, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = "Rejection Tag"
        verbose_name_plural = "Rejection Tags"

    def __str__(self):
        return self.name


class AcceptanceTag(models.Model):
    """Predefined acceptance/selection reasons"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.CharField(max_length=300, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = "Acceptance Tag"
        verbose_name_plural = "Acceptance Tags"

    def __str__(self):
        return self.name


class ApplicationRemark(models.Model):
    """Structured remarks when company accepts/rejects/shortlists a candidate"""
    REMARK_TYPE_CHOICES = (
        ('rejection', 'Rejection'),
        ('acceptance', 'Acceptance'),
        ('shortlist', 'Shortlist'),
        ('on_hold', 'On Hold'),
        ('general', 'General Note'),
    )

    job_application = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE,
        related_name='remarks', null=True, blank=True,
    )
    internship_application = models.ForeignKey(
        Application, on_delete=models.CASCADE,
        related_name='remarks', null=True, blank=True,
    )
    remark_type = models.CharField(max_length=20, choices=REMARK_TYPE_CHOICES)
    rejection_tags = models.ManyToManyField(RejectionTag, blank=True, related_name='remarks')
    acceptance_tags = models.ManyToManyField(AcceptanceTag, blank=True, related_name='remarks')
    custom_remarks = models.TextField(blank=True, help_text="Custom HR notes and remarks")
    hr_notes = models.TextField(blank=True, help_text="Internal HR notes (not visible to candidate)")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Application Remark"
        verbose_name_plural = "Application Remarks"

    def __str__(self):
        app = self.job_application or self.internship_application
        return f"{self.remark_type} remark for {app}"


class AutoScreeningResult(models.Model):
    """Stores detailed auto-screening breakdown per application"""
    job_application = models.OneToOneField(
        JobApplication, on_delete=models.CASCADE,
        related_name='screening_result', null=True, blank=True,
    )
    internship_application = models.OneToOneField(
        Application, on_delete=models.CASCADE,
        related_name='screening_result', null=True, blank=True,
    )
    skill_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    course_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gpa_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    experience_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    location_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    english_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    internet_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    profile_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    assessment_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    suggested_status = models.CharField(max_length=20, blank=True)
    matching_skills = models.TextField(blank=True, help_text="Comma-separated matching skills")
    missing_skills = models.TextField(blank=True, help_text="Comma-separated missing skills")
    skill_gaps = models.TextField(blank=True, help_text="Suggested skills to learn")
    screened_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Auto Screening Result"
        verbose_name_plural = "Auto Screening Results"

    def __str__(self):
        app = self.job_application or self.internship_application
        return f"Screening: {app} - {self.total_score}%"


class CandidateFeedback(models.Model):
    """Transparency feedback visible to candidates about their application"""
    job_application = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE,
        related_name='feedback', null=True, blank=True,
    )
    internship_application = models.ForeignKey(
        Application, on_delete=models.CASCADE,
        related_name='feedback', null=True, blank=True,
    )
    feedback_type = models.CharField(max_length=20, choices=(
        ('rejection_reason', 'Rejection Reason'),
        ('skill_gap', 'Skill Gap Suggestion'),
        ('improvement', 'Improvement Suggestion'),
        ('general', 'General Feedback'),
    ))
    message = models.TextField()
    suggested_skills = models.CharField(max_length=500, blank=True, help_text="Comma-separated skills to improve")
    is_visible = models.BooleanField(default=True, help_text="Visible to candidate")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Candidate Feedback"
        verbose_name_plural = "Candidate Feedback"

    def __str__(self):
        app = self.job_application or self.internship_application
        return f"Feedback for {app}"
