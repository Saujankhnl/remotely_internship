import logging
from decimal import Decimal

from django.db.models import Q

logger = logging.getLogger(__name__)

ENGLISH_LEVELS = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'fluent': 4, 'native': 5}
INTERNET_LEVELS = {'poor': 1, 'average': 2, 'good': 3, 'excellent': 4}
EXP_MAP = {'fresher': 0, 'junior': 1, 'mid': 3, 'senior': 5, 'lead': 8}


def _get_profile(application):
    """Get UserProfile for the applicant."""
    try:
        return application.applicant.user_profile
    except Exception:
        return None


def _get_post(application):
    """Get the job or internship post from an application."""
    from internships.models import JobApplication
    if isinstance(application, JobApplication):
        return application.job
    return application.internship


def _parse_skills(skills_str):
    """Parse comma-separated skills string into a lowercase set."""
    if not skills_str:
        return set()
    return set(s.strip().lower() for s in skills_str.split(',') if s.strip())


def _skill_score(profile, post):
    """Calculate skill match percentage."""
    post_skills = _parse_skills(post.required_skills)
    if not post_skills:
        return 100.0, set(), set()
    user_skills = _parse_skills(profile.skills) if profile else set()
    matching = post_skills & user_skills
    missing = post_skills - user_skills
    score = (len(matching) / len(post_skills)) * 100
    return score, matching, missing


def _course_score(profile, post):
    """Calculate course/degree match score."""
    required = getattr(post, 'required_course', '') or ''
    if not required.strip():
        return 100.0
    user_course = (profile.course if profile else '') or ''
    if not user_course.strip():
        return 0.0
    required_lower = required.strip().lower()
    user_lower = user_course.strip().lower()
    if required_lower == user_lower:
        return 100.0
    if required_lower in user_lower or user_lower in required_lower:
        return 75.0
    # Partial word matching
    req_words = set(required_lower.split())
    user_words = set(user_lower.split())
    overlap = req_words & user_words
    if overlap:
        return (len(overlap) / len(req_words)) * 60
    return 0.0


def _gpa_score(profile, post):
    """Calculate GPA score."""
    min_gpa = getattr(post, 'min_gpa', None)
    if not min_gpa:
        return 100.0
    user_gpa = profile.gpa if profile else None
    if not user_gpa:
        return 0.0
    if user_gpa >= min_gpa:
        return 100.0
    ratio = float(user_gpa / min_gpa)
    return max(0, ratio * 100)


def _experience_score(application, post):
    """Calculate experience match score."""
    from internships.models import JobApplication
    if isinstance(application, JobApplication):
        required_level = getattr(post, 'experience_level', '')
        required_years = EXP_MAP.get(required_level, 0)
        actual_years = application.years_of_experience or 0
    else:
        exp_str = getattr(post, 'experience', '') or ''
        try:
            required_years = int(''.join(filter(str.isdigit, exp_str)) or '0')
        except ValueError:
            required_years = 0
        actual_years = 0  # Internship applications don't have years_of_experience

    if required_years == 0:
        return 100.0 if actual_years > 0 else 50.0
    return min(100.0, (actual_years / required_years) * 100)


def _location_score(profile, post):
    """Calculate location match score."""
    preferred = getattr(post, 'preferred_location', '') or ''
    if not preferred.strip():
        is_remote = getattr(post, 'is_remote', False)
        if is_remote:
            return 100.0
        return 50.0  # No preference specified
    user_loc = (profile.location if profile else '') or ''
    if not user_loc.strip():
        return 0.0
    preferred_lower = preferred.strip().lower()
    user_lower = user_loc.strip().lower()
    if preferred_lower == user_lower:
        return 100.0
    if preferred_lower in user_lower or user_lower in preferred_lower:
        return 80.0
    return 0.0


def _english_score(profile, post):
    """Calculate English level match score."""
    preferred = getattr(post, 'preferred_english_level', '') or ''
    if not preferred.strip():
        return 100.0
    user_level = (profile.english_level if profile else '') or ''
    if not user_level.strip():
        return 0.0
    required_val = ENGLISH_LEVELS.get(preferred, 0)
    user_val = ENGLISH_LEVELS.get(user_level, 0)
    if required_val == 0:
        return 100.0
    if user_val >= required_val:
        return 100.0
    return (user_val / required_val) * 100


def _internet_score(profile, post):
    """Calculate internet quality match score."""
    preferred = getattr(post, 'preferred_internet_quality', '') or ''
    if not preferred.strip():
        return 100.0
    user_quality = (profile.internet_quality if profile else '') or ''
    if not user_quality.strip():
        return 0.0
    required_val = INTERNET_LEVELS.get(preferred, 0)
    user_val = INTERNET_LEVELS.get(user_quality, 0)
    if required_val == 0:
        return 100.0
    if user_val >= required_val:
        return 100.0
    return (user_val / required_val) * 100


def _profile_completeness_score(profile):
    """Get profile completeness score (0-100)."""
    if not profile:
        return 0.0
    return min(100.0, float(profile.completeness_score))


def _assessment_score(application, post):
    """Calculate assessment/badge score for matching skills."""
    from assessments.models import VerifiedBadge
    post_skills = _parse_skills(post.required_skills)
    if not post_skills:
        return 0.0
    badges = VerifiedBadge.objects.filter(
        user=application.applicant
    ).values_list('skill_name', flat=True)
    badge_skills = set(s.strip().lower() for s in badges)
    matching = post_skills & badge_skills
    if not post_skills:
        return 0.0
    return (len(matching) / len(post_skills)) * 100


def calculate_match_score(application):
    """
    Calculate comprehensive match score for an application.
    Returns a dict with individual scores and total.
    """
    profile = _get_profile(application)
    post = _get_post(application)
    is_premium = getattr(post, 'is_premium', False)

    # Calculate individual scores
    skill, matching_skills, missing_skills = _skill_score(profile, post)
    course = _course_score(profile, post)
    gpa = _gpa_score(profile, post)
    experience = _experience_score(application, post)
    location = _location_score(profile, post)
    english = _english_score(profile, post)
    internet = _internet_score(profile, post)
    profile_comp = _profile_completeness_score(profile)
    assessment = _assessment_score(application, post)

    # Weighted total
    if is_premium:
        total = (
            skill * 0.25 +
            course * 0.10 +
            gpa * 0.10 +
            experience * 0.15 +
            location * 0.05 +
            english * 0.10 +
            internet * 0.05 +
            profile_comp * 0.05 +
            assessment * 0.15
        )
    else:
        total = (
            skill * 0.30 +
            course * 0.10 +
            gpa * 0.10 +
            experience * 0.15 +
            location * 0.05 +
            english * 0.10 +
            internet * 0.05 +
            profile_comp * 0.05 +
            assessment * 0.10
        )

    # Auto-categorize
    if is_premium:
        if total >= 75:
            suggested = 'shortlisted'
        elif total >= 50:
            suggested = 'pending'
        else:
            suggested = 'rejected'
    else:
        if total >= 70:
            suggested = 'shortlisted'
        elif total >= 40:
            suggested = 'pending'
        else:
            suggested = 'rejected'

    # Generate skill gap suggestions
    skill_gaps = []
    for s in sorted(missing_skills):
        skill_gaps.append(f"Learn {s} to improve your match")

    return {
        'skill_score': round(skill, 2),
        'course_score': round(course, 2),
        'gpa_score': round(gpa, 2),
        'experience_score': round(experience, 2),
        'location_score': round(location, 2),
        'english_score': round(english, 2),
        'internet_score': round(internet, 2),
        'profile_score': round(profile_comp, 2),
        'assessment_score': round(assessment, 2),
        'total_score': round(total, 2),
        'suggested_status': suggested,
        'matching_skills': sorted(matching_skills),
        'missing_skills': sorted(missing_skills),
        'skill_gaps': skill_gaps,
    }


def auto_screen_application(application):
    """Run auto-screening on a single application and save results."""
    from internships.models import AutoScreeningResult

    scores = calculate_match_score(application)

    # Update application match score
    application.match_score = Decimal(str(scores['total_score']))
    application.auto_status = scores['suggested_status']
    application.save(update_fields=['match_score', 'auto_status'])

    # Create or update screening result
    from internships.models import JobApplication
    if isinstance(application, JobApplication):
        result, _ = AutoScreeningResult.objects.update_or_create(
            job_application=application,
            defaults={
                'skill_score': scores['skill_score'],
                'course_score': scores['course_score'],
                'gpa_score': scores['gpa_score'],
                'experience_score': scores['experience_score'],
                'location_score': scores['location_score'],
                'english_score': scores['english_score'],
                'internet_score': scores['internet_score'],
                'profile_score': scores['profile_score'],
                'assessment_score': scores['assessment_score'],
                'total_score': scores['total_score'],
                'suggested_status': scores['suggested_status'],
                'matching_skills': ', '.join(scores['matching_skills']),
                'missing_skills': ', '.join(scores['missing_skills']),
                'skill_gaps': '\n'.join(scores['skill_gaps']),
            }
        )
    else:
        result, _ = AutoScreeningResult.objects.update_or_create(
            internship_application=application,
            defaults={
                'skill_score': scores['skill_score'],
                'course_score': scores['course_score'],
                'gpa_score': scores['gpa_score'],
                'experience_score': scores['experience_score'],
                'location_score': scores['location_score'],
                'english_score': scores['english_score'],
                'internet_score': scores['internet_score'],
                'profile_score': scores['profile_score'],
                'assessment_score': scores['assessment_score'],
                'total_score': scores['total_score'],
                'suggested_status': scores['suggested_status'],
                'matching_skills': ', '.join(scores['matching_skills']),
                'missing_skills': ', '.join(scores['missing_skills']),
                'skill_gaps': '\n'.join(scores['skill_gaps']),
            }
        )

    return result


def bulk_screen_applications(post):
    """Screen all pending applications for a job/internship post."""
    from internships.models import Job, Internship, JobApplication, Application

    if isinstance(post, Job):
        applications = JobApplication.objects.filter(
            job=post, status='pending'
        ).select_related('applicant__user_profile')
    else:
        applications = Application.objects.filter(
            internship=post, status='pending'
        ).select_related('applicant__user_profile')

    results = []
    for app in applications:
        try:
            result = auto_screen_application(app)
            results.append(result)
        except Exception as e:
            logger.error(f"Screening failed for application {app.pk}: {e}")

    return results


def apply_auto_screening(post):
    """
    Screen and automatically update statuses for pending applications.
    Only changes status if auto_screen_enabled is True on the post.
    """
    if not getattr(post, 'auto_screen_enabled', False):
        return []

    from internships.models import Job, JobApplication, Application, StatusChange

    if isinstance(post, Job):
        applications = JobApplication.objects.filter(
            job=post, status='pending'
        ).select_related('applicant__user_profile')
    else:
        applications = Application.objects.filter(
            internship=post, status='pending'
        ).select_related('applicant__user_profile')

    updated = []
    for app in applications:
        try:
            result = auto_screen_application(app)
            suggested = result.suggested_status
            if suggested and suggested != app.status:
                old_status = app.status
                app.status = suggested
                app.save(update_fields=['status'])
                # Record status change
                if isinstance(post, Job):
                    StatusChange.objects.create(
                        job_application=app,
                        old_status=old_status,
                        new_status=suggested,
                        note=f"Auto-screened (score: {result.total_score}%)",
                    )
                else:
                    StatusChange.objects.create(
                        internship_application=app,
                        old_status=old_status,
                        new_status=suggested,
                        note=f"Auto-screened (score: {result.total_score}%)",
                    )
                updated.append(app)
        except Exception as e:
            logger.error(f"Auto-screening failed for application {app.pk}: {e}")

    return updated
