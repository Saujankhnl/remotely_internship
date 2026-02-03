import logging
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)


def get_status_message(new_status):
    """Return a professional message based on the new application status."""
    messages = {
        'pending': 'Your application is currently under review. We will notify you of any updates.',
        'reviewing': 'Great news! Your application is being actively reviewed by our team.',
        'shortlisted': 'Congratulations! You have been shortlisted for this position. We will contact you soon with next steps.',
        'interview': 'Congratulations! We would like to invite you for an interview. Please check your email for scheduling details.',
        'accepted': 'Congratulations! We are pleased to inform you that your application has been accepted. Welcome to the team!',
        'rejected': 'Thank you for your interest. After careful consideration, we have decided to move forward with other candidates. We encourage you to apply for future opportunities.',
        'withdrawn': 'Your application has been withdrawn as requested.',
    }
    return messages.get(new_status.lower(), 'Your application status has been updated.')


def send_application_status_email(application, old_status, new_status):
    """
    Send email notification when application status changes.
    
    Args:
        application: JobApplication or Application object
        old_status: Previous status string
        new_status: New status string
    """
    try:
        job_title = getattr(application, 'job', None) or getattr(application, 'internship', None)
        if hasattr(job_title, 'title'):
            title = job_title.title
            company = getattr(job_title, 'company', 'the company')
            if hasattr(company, 'name'):
                company_name = company.name
            else:
                company_name = str(company)
        else:
            title = str(job_title)
            company_name = 'the company'

        applicant_email = application.applicant.email
        applicant_name = getattr(application.applicant, 'get_full_name', lambda: application.applicant.username)()

        subject = f"Application Status Update - {title}"
        status_message = get_status_message(new_status)

        plain_message = f"""
Dear {applicant_name},

Your application status has been updated.

Position: {title}
Company: {company_name}
Previous Status: {old_status}
New Status: {new_status}

{status_message}

Best regards,
The Remotely Internship Team
        """.strip()

        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4A90A4; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .status-box {{ background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .status-label {{ font-weight: bold; color: #666; }}
        .old-status {{ color: #999; }}
        .new-status {{ color: #4A90A4; font-weight: bold; }}
        .message {{ padding: 15px; background-color: #e8f4f8; border-left: 4px solid #4A90A4; margin: 15px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Application Status Update</h1>
        </div>
        <div class="content">
            <p>Dear {applicant_name},</p>
            <p>Your application status has been updated.</p>
            
            <div class="status-box">
                <p><span class="status-label">Position:</span> {title}</p>
                <p><span class="status-label">Company:</span> {company_name}</p>
                <p><span class="status-label">Previous Status:</span> <span class="old-status">{old_status}</span></p>
                <p><span class="status-label">New Status:</span> <span class="new-status">{new_status}</span></p>
            </div>
            
            <div class="message">
                <p>{status_message}</p>
            </div>
            
            <p>Best regards,<br>The Remotely Internship Team</p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply directly to this email.</p>
        </div>
    </div>
</body>
</html>
        """.strip()

        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[applicant_email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Application status email sent to {applicant_email} for {title}")
        return True

    except Exception as e:
        logger.exception(f"Failed to send application status email: {e}")
        return False


def send_interview_scheduled_email(interview):
    """
    Send email notification when an interview is scheduled.
    
    Args:
        interview: Interview object with date, time, type, location/link, duration, notes
    """
    try:
        application = interview.application
        job_title = getattr(application, 'job', None) or getattr(application, 'internship', None)
        if hasattr(job_title, 'title'):
            title = job_title.title
            company = getattr(job_title, 'company', 'the company')
            if hasattr(company, 'name'):
                company_name = company.name
            else:
                company_name = str(company)
        else:
            title = str(job_title)
            company_name = 'the company'

        applicant_email = application.applicant.email
        applicant_name = getattr(application.applicant, 'get_full_name', lambda: application.applicant.username)()

        interview_date = interview.scheduled_at.strftime('%B %d, %Y')
        interview_time = interview.scheduled_at.strftime('%I:%M %p')
        interview_type = interview.get_interview_type_display()
        duration = f"{interview.duration_minutes} minutes"
        location = interview.location or ''
        meeting_link = ''
        notes = interview.notes or ''

        subject = f"Interview Scheduled - {title} at {company_name}"

        location_info = meeting_link if meeting_link else location if location else 'To be confirmed'

        plain_message = f"""
Dear {applicant_name},

Congratulations! An interview has been scheduled for your application.

Position: {title}
Company: {company_name}

Interview Details:
- Date: {interview_date}
- Time: {interview_time}
- Type: {interview_type}
- Duration: {duration}
- Location/Link: {location_info}

{f"Additional Notes: {notes}" if notes else ""}

Please ensure you are available at the scheduled time. If you need to reschedule, please contact us as soon as possible.

Best regards,
The Remotely Internship Team
        """.strip()

        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .details-box {{ background-color: white; padding: 20px; border-radius: 5px; margin: 15px 0; border: 1px solid #ddd; }}
        .detail-row {{ padding: 8px 0; border-bottom: 1px solid #eee; }}
        .detail-row:last-child {{ border-bottom: none; }}
        .detail-label {{ font-weight: bold; color: #666; display: inline-block; width: 120px; }}
        .notes {{ padding: 15px; background-color: #fff3cd; border-left: 4px solid #ffc107; margin: 15px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        .highlight {{ color: #28a745; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Interview Scheduled!</h1>
        </div>
        <div class="content">
            <p>Dear {applicant_name},</p>
            <p>Congratulations! An interview has been scheduled for your application to <span class="highlight">{title}</span> at <span class="highlight">{company_name}</span>.</p>
            
            <div class="details-box">
                <h3 style="margin-top: 0;">Interview Details</h3>
                <div class="detail-row">
                    <span class="detail-label">Date:</span> {interview_date}
                </div>
                <div class="detail-row">
                    <span class="detail-label">Time:</span> {interview_time}
                </div>
                <div class="detail-row">
                    <span class="detail-label">Type:</span> {interview_type}
                </div>
                <div class="detail-row">
                    <span class="detail-label">Duration:</span> {duration}
                </div>
                <div class="detail-row">
                    <span class="detail-label">Location/Link:</span> {location_info}
                </div>
            </div>
            
            {f'<div class="notes"><strong>Additional Notes:</strong><br>{notes}</div>' if notes else ''}
            
            <p>Please ensure you are available at the scheduled time. If you need to reschedule, please contact us as soon as possible.</p>
            
            <p>Best regards,<br>The Remotely Internship Team</p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply directly to this email.</p>
        </div>
    </div>
</body>
</html>
        """.strip()

        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[applicant_email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Interview scheduled email sent to {applicant_email} for {title}")
        return True

    except Exception as e:
        logger.exception(f"Failed to send interview scheduled email: {e}")
        return False


def send_new_job_alert_email(user, matching_jobs):
    """
    Send email to users about new jobs matching their skills.
    
    Args:
        user: User object
        matching_jobs: QuerySet or list of Job/Internship objects
    """
    try:
        if not matching_jobs:
            return False

        user_email = user.email
        user_name = getattr(user, 'get_full_name', lambda: user.username)()

        subject = f"New Job Opportunities Matching Your Skills"

        jobs_plain = []
        jobs_html = []

        for job in matching_jobs:
            title = job.title
            company = getattr(job, 'company', 'Company')
            if hasattr(company, 'name'):
                company_name = company.name
            else:
                company_name = str(company)
            location = getattr(job, 'location', 'Remote')
            job_id = getattr(job, 'id', '')
            job_url = f"{settings.SITE_URL}/internships/{job_id}/" if hasattr(settings, 'SITE_URL') else f"/internships/{job_id}/"

            jobs_plain.append(f"- {title} at {company_name} ({location})\n  Apply: {job_url}")
            jobs_html.append(f"""
                <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 10px 0; border: 1px solid #ddd;">
                    <h3 style="margin: 0 0 10px 0; color: #4A90A4;">{title}</h3>
                    <p style="margin: 5px 0;"><strong>Company:</strong> {company_name}</p>
                    <p style="margin: 5px 0;"><strong>Location:</strong> {location}</p>
                    <a href="{job_url}" style="display: inline-block; padding: 8px 16px; background-color: #4A90A4; color: white; text-decoration: none; border-radius: 4px; margin-top: 10px;">View & Apply</a>
                </div>
            """)

        plain_message = f"""
Dear {user_name},

We found new job opportunities that match your skills!

{chr(10).join(jobs_plain)}

Don't miss out on these opportunities. Apply now!

Best regards,
The Remotely Internship Team
        """.strip()

        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4A90A4; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>New Job Opportunities For You!</h1>
        </div>
        <div class="content">
            <p>Dear {user_name},</p>
            <p>We found <strong>{len(matching_jobs)}</strong> new job opportunities that match your skills!</p>
            
            {''.join(jobs_html)}
            
            <p style="margin-top: 20px;">Don't miss out on these opportunities. Apply now!</p>
            
            <p>Best regards,<br>The Remotely Internship Team</p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply directly to this email.</p>
            <p>To update your job preferences, visit your profile settings.</p>
        </div>
    </div>
</body>
</html>
        """.strip()

        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)

        logger.info(f"New job alert email sent to {user_email} with {len(matching_jobs)} jobs")
        return True

    except Exception as e:
        logger.exception(f"Failed to send new job alert email: {e}")
        return False
