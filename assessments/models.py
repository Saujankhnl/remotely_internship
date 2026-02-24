from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class SkillAssessment(models.Model):
    skill_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    time_limit_minutes = models.PositiveIntegerField(default=30)
    passing_score = models.PositiveIntegerField(default=70, help_text="Passing percentage")
    max_attempts = models.PositiveIntegerField(default=3)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.skill_name

    class Meta:
        verbose_name = "Skill Assessment"
        verbose_name_plural = "Skill Assessments"


class Question(models.Model):
    OPTION_CHOICES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    )
    assessment = models.ForeignKey(SkillAssessment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES)
    explanation = models.TextField(blank=True, help_text="Explanation shown after attempt")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:60]}"


class AssessmentAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assessment_attempts')
    assessment = models.ForeignKey(SkillAssessment, on_delete=models.CASCADE, related_name='attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    passed = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-started_at']
        verbose_name = "Assessment Attempt"
        verbose_name_plural = "Assessment Attempts"

    def __str__(self):
        return f"{self.user.username} - {self.assessment.skill_name} ({self.started_at:%Y-%m-%d})"

    @property
    def is_timed_out(self):
        if self.is_completed:
            return False
        deadline = self.started_at + timedelta(minutes=self.assessment.time_limit_minutes)
        return timezone.now() > deadline

    @property
    def time_remaining_seconds(self):
        if self.is_completed:
            return 0
        deadline = self.started_at + timedelta(minutes=self.assessment.time_limit_minutes)
        remaining = (deadline - timezone.now()).total_seconds()
        return max(0, int(remaining))


class AttemptAnswer(models.Model):
    OPTION_CHOICES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    )
    attempt = models.ForeignKey(AssessmentAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, choices=OPTION_CHOICES, blank=True)
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Attempt Answer"
        verbose_name_plural = "Attempt Answers"

    def __str__(self):
        return f"Answer for Q{self.question.order} by {self.attempt.user.username}"


class VerifiedBadge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='verified_badges')
    assessment = models.ForeignKey(SkillAssessment, on_delete=models.CASCADE, related_name='badges')
    skill_name = models.CharField(max_length=100)
    earned_at = models.DateTimeField(auto_now_add=True)
    score = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        unique_together = ['user', 'assessment']
        verbose_name = "Verified Badge"
        verbose_name_plural = "Verified Badges"

    def __str__(self):
        return f"{self.user.username} - {self.skill_name} Badge"
