from django.contrib import admin
from .models import SkillAssessment, Question, AssessmentAttempt, AttemptAnswer, VerifiedBadge


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ('order', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'explanation')


@admin.register(SkillAssessment)
class SkillAssessmentAdmin(admin.ModelAdmin):
    list_display = ('skill_name', 'time_limit_minutes', 'passing_score', 'max_attempts', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('skill_name', 'description')
    inlines = [QuestionInline]


class AttemptAnswerInline(admin.TabularInline):
    model = AttemptAnswer
    extra = 0
    readonly_fields = ('question', 'selected_option', 'is_correct')


@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'assessment', 'score', 'total_questions', 'percentage', 'passed', 'is_completed', 'started_at')
    list_filter = ('passed', 'is_completed', 'assessment', 'started_at')
    search_fields = ('user__username', 'user__email', 'assessment__skill_name')
    readonly_fields = ('started_at',)
    inlines = [AttemptAnswerInline]


@admin.register(VerifiedBadge)
class VerifiedBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill_name', 'score', 'earned_at')
    list_filter = ('skill_name', 'earned_at')
    search_fields = ('user__username', 'user__email', 'skill_name')
    readonly_fields = ('earned_at',)
