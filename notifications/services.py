from django.urls import reverse

from .models import Notification


def notify_application_status_change(application, new_status):
    """Notify applicant when their application status changes."""
    from internships.models import JobApplication, Application

    status_display = dict(application.STATUS_CHOICES).get(new_status, new_status)

    if isinstance(application, JobApplication):
        message = (
            f'Your application for "{application.job.title}" has been '
            f'updated to: {status_display}'
        )
        related_url = reverse(
            'internships:job_application_detail', args=[application.pk]
        )
    elif isinstance(application, Application):
        message = (
            f'Your application for "{application.internship.title}" has been '
            f'updated to: {status_display}'
        )
        related_url = reverse(
            'internships:application_detail', args=[application.pk]
        )
    else:
        return None

    return Notification.create_notification(
        user=application.applicant,
        message=message,
        notification_type='application_status',
        related_object_id=application.pk,
        related_url=related_url,
    )


def notify_interview_scheduled(interview):
    """Notify applicant when an interview is scheduled."""
    application = interview.application
    scheduled_time = interview.scheduled_at.strftime('%b %d, %Y at %I:%M %p')
    interview_type = interview.get_interview_type_display()

    message = (
        f'{interview_type} interview scheduled for "{application.job.title}" '
        f'on {scheduled_time}'
    )
    related_url = reverse('internships:my_interviews')

    return Notification.create_notification(
        user=application.applicant,
        message=message,
        notification_type='interview_scheduled',
        related_object_id=interview.pk,
        related_url=related_url,
    )


def notify_profile_viewed(profile_owner, viewer):
    """Notify user when a company views their profile."""
    viewer_name = viewer.username
    if hasattr(viewer, 'company_profile') and viewer.company_profile.company_name:
        viewer_name = viewer.company_profile.company_name

    message = f'{viewer_name} viewed your profile'
    related_url = reverse(
        'accounts:public_user_profile', args=[profile_owner.username]
    )

    return Notification.create_notification(
        user=profile_owner,
        message=message,
        notification_type='profile_viewed',
        related_url=related_url,
    )


def notify_job_match(user, job):
    """Notify user when a new job matches their skills."""
    message = f'New job matching your skills: "{job.title}"'
    related_url = reverse('internships:job_detail', args=[job.pk])

    return Notification.create_notification(
        user=user,
        message=message,
        notification_type='job_match',
        related_object_id=job.pk,
        related_url=related_url,
    )


def notify_new_application(application):
    """Notify company when someone applies to their job/internship."""
    from internships.models import JobApplication, Application

    if isinstance(application, JobApplication):
        job = application.job
        message = (
            f'{application.full_name} applied for your job posting: '
            f'"{job.title}"'
        )
        related_url = reverse(
            'internships:job_application_detail', args=[application.pk]
        )
        company_user = job.company
    elif isinstance(application, Application):
        internship = application.internship
        message = (
            f'{application.full_name} applied for your internship: '
            f'"{internship.title}"'
        )
        related_url = reverse(
            'internships:application_detail', args=[application.pk]
        )
        company_user = internship.company
    else:
        return None

    return Notification.create_notification(
        user=company_user,
        message=message,
        notification_type='new_application',
        related_object_id=application.pk,
        related_url=related_url,
    )
