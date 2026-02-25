from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Max, Count
from .models import SkillAssessment, Question, AssessmentAttempt, AttemptAnswer, VerifiedBadge
from accounts.decorators import user_required


@login_required
@user_required
def assessment_list(request):
    assessments = SkillAssessment.objects.filter(is_active=True).annotate(
        question_count=Count('questions'),
    )

    user_badges = set(
        VerifiedBadge.objects.filter(user=request.user).values_list('assessment_id', flat=True)
    )

    user_attempts = {}
    user_best_scores = {}
    attempts_qs = AssessmentAttempt.objects.filter(
        user=request.user, is_completed=True
    ).values('assessment_id').annotate(
        attempt_count=Count('id'),
        best_score=Max('percentage'),
    )
    for entry in attempts_qs:
        user_attempts[entry['assessment_id']] = entry['attempt_count']
        user_best_scores[entry['assessment_id']] = entry['best_score']

    assessment_data = []
    for a in assessments:
        assessment_data.append({
            'assessment': a,
            'attempt_count': user_attempts.get(a.id, 0),
            'best_score': user_best_scores.get(a.id, None),
            'has_badge': a.id in user_badges,
            'attempts_remaining': a.max_attempts - user_attempts.get(a.id, 0),
        })

    return render(request, 'assessments/assessment_list.html', {
        'assessment_data': assessment_data,
    })


@login_required
@user_required
def assessment_detail(request, pk):
    assessment = get_object_or_404(
        SkillAssessment.objects.annotate(question_count=Count('questions')),
        pk=pk, is_active=True,
    )

    user_attempts = AssessmentAttempt.objects.filter(
        user=request.user, assessment=assessment, is_completed=True,
    ).select_related('assessment')

    attempt_count = user_attempts.count()
    attempts_remaining = assessment.max_attempts - attempt_count
    best_score = user_attempts.aggregate(best=Max('percentage'))['best']
    has_badge = VerifiedBadge.objects.filter(user=request.user, assessment=assessment).exists()

    # Check for an in-progress attempt
    in_progress = AssessmentAttempt.objects.filter(
        user=request.user, assessment=assessment, is_completed=False,
    ).first()

    return render(request, 'assessments/assessment_detail.html', {
        'assessment': assessment,
        'user_attempts': user_attempts,
        'attempt_count': attempt_count,
        'attempts_remaining': attempts_remaining,
        'best_score': best_score,
        'has_badge': has_badge,
        'in_progress': in_progress,
    })


@login_required
@user_required
@require_POST
def start_assessment(request, pk):
    assessment = get_object_or_404(SkillAssessment, pk=pk, is_active=True)

    # Check for existing in-progress attempt
    existing = AssessmentAttempt.objects.filter(
        user=request.user, assessment=assessment, is_completed=False,
    ).first()
    if existing:
        if existing.is_timed_out:
            _finalize_attempt(existing)
            messages.info(request, "Your previous attempt timed out and has been submitted.")
        else:
            return redirect('assessments:take_assessment', attempt_id=existing.id)

    # Check attempts remaining
    completed_count = AssessmentAttempt.objects.filter(
        user=request.user, assessment=assessment, is_completed=True,
    ).count()
    if completed_count >= assessment.max_attempts:
        messages.error(request, "You have reached the maximum number of attempts for this assessment.")
        return redirect('assessments:assessment_detail', pk=pk)

    # Create attempt
    questions = list(assessment.questions.all().order_by('?'))
    if not questions:
        messages.error(request, "This assessment has no questions yet.")
        return redirect('assessments:assessment_detail', pk=pk)

    attempt = AssessmentAttempt.objects.create(
        user=request.user,
        assessment=assessment,
        total_questions=len(questions),
    )

    # Create blank answers
    AttemptAnswer.objects.bulk_create([
        AttemptAnswer(attempt=attempt, question=q) for q in questions
    ])

    return redirect('assessments:take_assessment', attempt_id=attempt.id)


@login_required
@user_required
def take_assessment(request, attempt_id):
    attempt = get_object_or_404(
        AssessmentAttempt.objects.select_related('assessment'),
        pk=attempt_id, user=request.user,
    )

    if attempt.is_completed:
        return redirect('assessments:assessment_result', attempt_id=attempt.id)

    # Auto-finalize if timed out on GET
    if attempt.is_timed_out:
        _finalize_attempt(attempt)
        messages.info(request, "Time's up! Your answers have been submitted automatically.")
        return redirect('assessments:assessment_result', attempt_id=attempt.id)

    answers = attempt.answers.select_related('question').order_by('question__order')

    if request.method == 'POST':
        _process_submission(attempt, answers, request.POST)
        return redirect('assessments:assessment_result', attempt_id=attempt.id)

    return render(request, 'assessments/take_assessment.html', {
        'attempt': attempt,
        'answers': answers,
        'time_remaining': attempt.time_remaining_seconds,
    })


@login_required
@user_required
def assessment_result(request, attempt_id):
    attempt = get_object_or_404(
        AssessmentAttempt.objects.select_related('assessment'),
        pk=attempt_id, user=request.user, is_completed=True,
    )
    answers = attempt.answers.select_related('question').order_by('question__order')
    has_badge = VerifiedBadge.objects.filter(user=request.user, assessment=attempt.assessment).exists()

    return render(request, 'assessments/assessment_result.html', {
        'attempt': attempt,
        'answers': answers,
        'has_badge': has_badge,
    })


@login_required
@user_required
def my_badges(request):
    badges = VerifiedBadge.objects.filter(user=request.user).select_related('assessment').order_by('-earned_at')
    return render(request, 'assessments/my_badges.html', {
        'badges': badges,
    })


# ---------- helpers ----------

def _process_submission(attempt, answers, post_data):
    """Score the attempt, award badge if passed."""
    # Check timeout - if timed out, still score what's answered
    correct_count = 0
    for answer in answers:
        selected = post_data.get(f'question_{answer.question_id}', '')
        if selected in ('A', 'B', 'C', 'D'):
            answer.selected_option = selected
            answer.is_correct = selected == answer.question.correct_option
            if answer.is_correct:
                correct_count += 1
            answer.save(update_fields=['selected_option', 'is_correct'])

    total = attempt.total_questions
    percentage = (correct_count / total * 100) if total > 0 else 0

    attempt.score = correct_count
    attempt.percentage = round(percentage, 2)
    attempt.passed = percentage >= attempt.assessment.passing_score
    attempt.is_completed = True
    attempt.completed_at = timezone.now()
    attempt.save(update_fields=['score', 'percentage', 'passed', 'is_completed', 'completed_at'])

    # Award badge if passed and not already earned
    if attempt.passed:
        VerifiedBadge.objects.get_or_create(
            user=attempt.user,
            assessment=attempt.assessment,
            defaults={
                'skill_name': attempt.assessment.skill_name,
                'score': attempt.percentage,
            },
        )


def _finalize_attempt(attempt):
    """Finalize a timed-out attempt by scoring whatever was answered."""
    answers = attempt.answers.select_related('question').all()
    correct_count = sum(1 for a in answers if a.selected_option and a.selected_option == a.question.correct_option)
    for a in answers:
        if a.selected_option:
            a.is_correct = a.selected_option == a.question.correct_option
            a.save(update_fields=['is_correct'])

    total = attempt.total_questions
    percentage = (correct_count / total * 100) if total > 0 else 0

    attempt.score = correct_count
    attempt.percentage = round(percentage, 2)
    attempt.passed = percentage >= attempt.assessment.passing_score
    attempt.is_completed = True
    attempt.completed_at = timezone.now()
    attempt.save(update_fields=['score', 'percentage', 'passed', 'is_completed', 'completed_at'])

    if attempt.passed:
        VerifiedBadge.objects.get_or_create(
            user=attempt.user,
            assessment=attempt.assessment,
            defaults={
                'skill_name': attempt.assessment.skill_name,
                'score': attempt.percentage,
            },
        )
