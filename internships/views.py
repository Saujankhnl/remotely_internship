from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, Http404, JsonResponse
from django.db.models import Q, Count
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from .models import Internship, Application, Job, JobApplication, JobBookmark, JobView, Interview, StatusChange
from .forms import InternshipForm, ApplicationForm, JobForm, JobApplicationForm, InterviewForm
from .emails import send_application_status_email, send_interview_scheduled_email
from accounts.decorators import company_approved_required, user_required, company_required
from notifications.services import (
    notify_application_status_change, notify_interview_scheduled,
    notify_new_application,
)


def _build_query_string(request):
    """Build query string from GET params excluding 'page'."""
    params = request.GET.copy()
    params.pop('page', None)
    return params.urlencode()


# ============ Public Views ============

def internship_list(request):
    """List all open internships with search/filter"""
    internships = Internship.objects.filter(status='open').select_related('company__company_profile')
    
    # Search
    query = request.GET.get('q', '')
    if query:
        internships = internships.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(required_skills__icontains=query) |
            Q(location__icontains=query) |
            Q(company__company_profile__company_name__icontains=query)
        )
    
    # Filter by type
    internship_type = request.GET.get('type', '')
    if internship_type in ['paid', 'unpaid']:
        internships = internships.filter(internship_type=internship_type)
    
    # Filter by location
    location = request.GET.get('location', '')
    if location:
        internships = internships.filter(location__icontains=location)
    
    # Filter by date posted
    date_posted = request.GET.get('date_posted', '')
    if date_posted == '24h':
        internships = internships.filter(created_at__gte=timezone.now() - timedelta(hours=24))
    elif date_posted == '7d':
        internships = internships.filter(created_at__gte=timezone.now() - timedelta(days=7))
    elif date_posted == '30d':
        internships = internships.filter(created_at__gte=timezone.now() - timedelta(days=30))
    
    # Pagination
    paginator = Paginator(internships, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'internships/internship_list.html', {
        'page_obj': page_obj,
        'query': query,
        'selected_type': internship_type,
        'selected_location': location,
        'selected_date_posted': date_posted,
        'query_string': _build_query_string(request),
    })


def internship_detail(request, pk):
    """View internship details"""
    internship = get_object_or_404(Internship, pk=pk)
    
    # Check if user has already applied
    has_applied = False
    if request.user.is_authenticated and request.user.user_type == 'user':
        has_applied = Application.objects.filter(
            internship=internship, 
            applicant=request.user
        ).exists()
    
    return render(request, 'internships/internship_detail.html', {
        'internship': internship,
        'has_applied': has_applied,
    })


# ============ Company Views ============

@company_approved_required
def create_internship(request):
    """Create a new internship posting"""
    if request.method == 'POST':
        form = InternshipForm(request.POST)
        if form.is_valid():
            internship = form.save(commit=False)
            internship.company = request.user
            internship.save()
            messages.success(request, 'Internship posted successfully!')
            return redirect('internships:my_internships')
    else:
        form = InternshipForm()
    
    return render(request, 'internships/create_internship.html', {'form': form})


@company_required
def edit_internship(request, pk):
    """Edit an existing internship"""
    internship = get_object_or_404(Internship, pk=pk, company=request.user)
    
    if request.method == 'POST':
        form = InternshipForm(request.POST, instance=internship)
        if form.is_valid():
            form.save()
            messages.success(request, 'Internship updated successfully!')
            return redirect('internships:my_internships')
    else:
        form = InternshipForm(instance=internship)
    
    return render(request, 'internships/edit_internship.html', {
        'form': form,
        'internship': internship
    })


@company_required
def delete_internship(request, pk):
    """Delete an internship"""
    internship = get_object_or_404(Internship, pk=pk, company=request.user)
    
    if request.method == 'POST':
        internship.delete()
        messages.success(request, 'Internship deleted successfully!')
        return redirect('internships:my_internships')
    
    return render(request, 'internships/delete_internship.html', {
        'internship': internship
    })


@company_approved_required
def toggle_internship_status(request, pk):
    """Toggle internship status between open and closed"""
    internship = get_object_or_404(Internship, pk=pk, company=request.user)
    
    if request.method == 'POST':
        internship.status = 'closed' if internship.status == 'open' else 'open'
        internship.save()
        status_msg = 'closed' if internship.status == 'closed' else 'reopened'
        messages.success(request, f'Internship {status_msg} successfully!')
    
    return redirect('internships:my_internships')


@company_required
def my_internships(request):
    """List company's own internships with application status breakdown"""
    internships = Internship.objects.filter(company=request.user).annotate(
        apps_count=Count('applications'),
        pending_count=Count('applications', filter=Q(applications__status='pending')),
        accepted_count=Count('applications', filter=Q(applications__status='accepted')),
        rejected_count=Count('applications', filter=Q(applications__status='rejected')),
    ).order_by('-created_at')
    
    return render(request, 'internships/my_internships.html', {
        'internships': internships
    })


@company_required
def view_applications(request, pk):
    """View all applications for a specific internship"""
    internship = get_object_or_404(Internship, pk=pk, company=request.user)
    applications = internship.applications.all()
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        applications = applications.filter(status=status)
    
    # Pagination
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'internships/view_applications.html', {
        'internship': internship,
        'page_obj': page_obj,
        'selected_status': status,
        'query_string': _build_query_string(request),
    })


@company_required
def application_detail(request, pk):
    """View detailed application"""
    application = get_object_or_404(Application, pk=pk)
    
    # Ensure the company owns the internship
    if application.internship.company != request.user:
        return HttpResponseForbidden("You don't have permission to view this application.")
    
    return render(request, 'internships/application_detail.html', {
        'application': application
    })


@company_required
def update_application_status(request, pk):
    """Update application status"""
    application = get_object_or_404(Application, pk=pk)
    
    if application.internship.company != request.user:
        return HttpResponseForbidden("You don't have permission to update this application.")
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Application.STATUS_CHOICES):
            old_status = application.status
            application.status = new_status
            application.save()
            StatusChange.objects.create(
                internship_application=application,
                old_status=old_status,
                new_status=new_status,
                changed_by=request.user,
            )
            notify_application_status_change(application, new_status)
            messages.success(request, f'Application status updated to {new_status}.')
    
    return redirect('internships:application_detail', pk=pk)


# ============ User Views ============

@user_required
def apply_internship(request, pk):
    """Apply for an internship"""
    internship = get_object_or_404(Internship, pk=pk, status='open')
    
    # Check if already applied
    if Application.objects.filter(internship=internship, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this internship.')
        return redirect('internships:internship_detail', pk=pk)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.internship = internship
            application.applicant = request.user
            application.save()
            notify_new_application(application)
            messages.success(request, 'Application submitted successfully!')
            return redirect('internships:my_applications')
    else:
        # Pre-fill form with user's profile data
        from accounts.models import UserProfile
        try:
            profile = UserProfile.objects.get(user=request.user)
            initial_data = {
                'full_name': profile.full_name,
                'email': request.user.email,
                'phone': profile.phone,
                'linkedin': profile.linkedin,
            }
        except UserProfile.DoesNotExist:
            initial_data = {'email': request.user.email}
        
        form = ApplicationForm(initial=initial_data)
    
    return render(request, 'internships/apply_internship.html', {
        'form': form,
        'internship': internship
    })


@user_required
def my_applications(request):
    """List user's applications"""
    applications = Application.objects.filter(applicant=request.user)
    
    return render(request, 'internships/my_applications.html', {
        'applications': applications
    })


@user_required
def withdraw_application(request, pk):
    """Withdraw an application"""
    application = get_object_or_404(Application, pk=pk, applicant=request.user)
    
    if request.method == 'POST':
        application.delete()
        messages.success(request, 'Application withdrawn successfully!')
        return redirect('internships:my_applications')
    
    return render(request, 'internships/withdraw_application.html', {
        'application': application
    })


# ==================== JOB VIEWS ====================

def job_list(request):
    """List all open jobs with search/filter"""
    jobs = Job.objects.filter(status='open').select_related('company__company_profile')
    
    # Search
    query = request.GET.get('q', '')
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(required_skills__icontains=query) |
            Q(location__icontains=query) |
            Q(company__company_profile__company_name__icontains=query)
        )
    
    # Filter by job type
    job_type = request.GET.get('type', '')
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    # Filter by experience level
    experience = request.GET.get('experience', '')
    if experience:
        jobs = jobs.filter(experience_level=experience)
    
    # Filter by remote
    remote = request.GET.get('remote', '')
    if remote == 'yes':
        jobs = jobs.filter(is_remote=True)
    
    # Filter by location
    location = request.GET.get('location', '')
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    # Filter by date posted
    date_posted = request.GET.get('date_posted', '')
    if date_posted == '24h':
        jobs = jobs.filter(created_at__gte=timezone.now() - timedelta(hours=24))
    elif date_posted == '7d':
        jobs = jobs.filter(created_at__gte=timezone.now() - timedelta(days=7))
    elif date_posted == '30d':
        jobs = jobs.filter(created_at__gte=timezone.now() - timedelta(days=30))
    
    # Filter by salary range
    salary_min = request.GET.get('salary_min', '')
    if salary_min:
        try:
            jobs = jobs.filter(salary_min__gte=int(salary_min))
        except ValueError:
            pass
    
    salary_max = request.GET.get('salary_max', '')
    if salary_max:
        try:
            jobs = jobs.filter(salary_max__lte=int(salary_max))
        except ValueError:
            pass
    
    # Pagination
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'internships/job_list.html', {
        'page_obj': page_obj,
        'query': query,
        'selected_type': job_type,
        'selected_experience': experience,
        'is_remote': remote,
        'selected_location': location,
        'selected_date_posted': date_posted,
        'selected_salary_min': salary_min,
        'selected_salary_max': salary_max,
        'query_string': _build_query_string(request),
    })


def job_detail(request, pk):
    """View job details with application stats for company owner"""
    job = get_object_or_404(Job, pk=pk)
    
    track_job_view(request, job)
    
    has_applied = False
    is_bookmarked = False
    app_stats = None
    
    if request.user.is_authenticated:
        if request.user.user_type == 'user':
            has_applied = JobApplication.objects.filter(
                job=job, 
                applicant=request.user
            ).exists()
        is_bookmarked = JobBookmark.objects.filter(user=request.user, job=job).exists()
        
        # Show application statistics to the job owner (company)
        if request.user == job.company:
            status_counts = job.job_applications.values('status').annotate(
                count=Count('id')
            )
            app_stats = {
                'total': sum(item['count'] for item in status_counts),
                'breakdown': {item['status']: item['count'] for item in status_counts},
            }
    
    return render(request, 'internships/job_detail.html', {
        'job': job,
        'has_applied': has_applied,
        'is_bookmarked': is_bookmarked,
        'app_stats': app_stats,
    })


@company_approved_required
def create_job(request):
    """Create a new job posting"""
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('internships:my_jobs')
    else:
        form = JobForm()
    
    return render(request, 'internships/create_job.html', {'form': form})


@company_required
def edit_job(request, pk):
    """Edit an existing job"""
    job = get_object_or_404(Job, pk=pk, company=request.user)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('internships:my_jobs')
    else:
        form = JobForm(instance=job)
    
    return render(request, 'internships/edit_job.html', {
        'form': form,
        'job': job
    })


@company_required
def delete_job(request, pk):
    """Delete a job"""
    job = get_object_or_404(Job, pk=pk, company=request.user)
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return redirect('internships:my_jobs')
    
    return render(request, 'internships/delete_job.html', {'job': job})


@company_approved_required
def toggle_job_status(request, pk):
    """Toggle job status between open and closed"""
    job = get_object_or_404(Job, pk=pk, company=request.user)
    
    if request.method == 'POST':
        job.status = 'closed' if job.status == 'open' else 'open'
        job.save()
        messages.success(request, f'Job {"closed" if job.status == "closed" else "reopened"} successfully!')
    
    return redirect('internships:my_jobs')


@company_required
def my_jobs(request):
    """List company's own jobs with application status breakdown"""
    jobs = Job.objects.filter(company=request.user).annotate(
        apps_count=Count('job_applications'),
        pending_count=Count('job_applications', filter=Q(job_applications__status='pending')),
        accepted_count=Count('job_applications', filter=Q(job_applications__status='accepted')),
        rejected_count=Count('job_applications', filter=Q(job_applications__status='rejected')),
        interview_count=Count('job_applications', filter=Q(job_applications__status='interview')),
    ).order_by('-created_at')
    
    return render(request, 'internships/my_jobs.html', {'jobs': jobs})


@company_required
def view_job_applications(request, pk):
    """View all applications for a specific job"""
    job = get_object_or_404(Job, pk=pk, company=request.user)
    applications = job.job_applications.all()
    
    status = request.GET.get('status', '')
    if status:
        applications = applications.filter(status=status)
    
    # Pagination
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'internships/view_job_applications.html', {
        'job': job,
        'page_obj': page_obj,
        'selected_status': status,
        'query_string': _build_query_string(request),
    })


@company_required
def job_application_detail(request, pk):
    """View detailed job application"""
    application = get_object_or_404(JobApplication, pk=pk)
    
    if application.job.company != request.user:
        raise PermissionDenied("You don't have permission to view this application.")
    
    return render(request, 'internships/job_application_detail.html', {
        'application': application
    })


@company_required
def update_job_application_status(request, pk):
    """Update job application status"""
    application = get_object_or_404(JobApplication, pk=pk)
    
    if application.job.company != request.user:
        raise PermissionDenied("You don't have permission to update this application.")
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(JobApplication.STATUS_CHOICES):
            old_status = application.status
            application.status = new_status
            application.save()
            StatusChange.objects.create(
                job_application=application,
                old_status=old_status,
                new_status=new_status,
                changed_by=request.user,
            )
            
            send_application_status_email(application, old_status, new_status)
            notify_application_status_change(application, new_status)
            
            messages.success(request, f'Application status updated to {new_status}.')
    
    return redirect('internships:job_application_detail', pk=pk)


@user_required
def apply_job(request, pk):
    """Apply for a job"""
    job = get_object_or_404(Job, pk=pk, status='open')
    
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('internships:job_detail', pk=pk)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            notify_new_application(application)
            messages.success(request, 'Application submitted successfully!')
            return redirect('internships:my_job_applications')
    else:
        from accounts.models import UserProfile
        try:
            profile = UserProfile.objects.get(user=request.user)
            initial_data = {
                'full_name': profile.full_name,
                'email': request.user.email,
                'phone': profile.phone,
                'linkedin': profile.linkedin,
            }
        except UserProfile.DoesNotExist:
            initial_data = {'email': request.user.email}
        
        form = JobApplicationForm(initial=initial_data)
    
    return render(request, 'internships/apply_job.html', {
        'form': form,
        'job': job
    })


@user_required
def my_job_applications(request):
    """List user's job applications"""
    applications = JobApplication.objects.filter(applicant=request.user)
    
    return render(request, 'internships/my_job_applications.html', {
        'applications': applications
    })


@user_required
def withdraw_job_application(request, pk):
    """Withdraw a job application"""
    application = get_object_or_404(JobApplication, pk=pk, applicant=request.user)
    
    if request.method == 'POST':
        application.delete()
        messages.success(request, 'Application withdrawn successfully!')
        return redirect('internships:my_job_applications')
    
    return render(request, 'internships/withdraw_job_application.html', {
        'application': application
    })


# ==================== BOOKMARK VIEWS ====================

@login_required
@require_POST
def toggle_job_bookmark(request, pk):
    """Toggle bookmark status for a job (AJAX)"""
    job = get_object_or_404(Job, pk=pk)
    bookmark, created = JobBookmark.objects.get_or_create(user=request.user, job=job)
    
    if not created:
        bookmark.delete()
        return JsonResponse({'bookmarked': False, 'message': 'Bookmark removed'})
    
    return JsonResponse({'bookmarked': True, 'message': 'Job bookmarked'})


@user_required
def saved_jobs(request):
    """List user's saved/bookmarked jobs"""
    bookmarks = JobBookmark.objects.filter(user=request.user).select_related('job', 'job__company')
    
    return render(request, 'internships/saved_jobs.html', {
        'bookmarks': bookmarks
    })


# ==================== JOB VIEWS TRACKING ====================

def track_job_view(request, job):
    """Helper function to track job views"""
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
    if ',' in ip_address:
        ip_address = ip_address.split(',')[0].strip()
    
    viewer = request.user if request.user.is_authenticated else None
    
    JobView.objects.create(
        job=job,
        viewer=viewer,
        ip_address=ip_address[:45] if ip_address else None
    )


# ==================== JOB RECOMMENDATIONS ====================

@user_required
def recommended_jobs(request):
    """Get job recommendations based on user's skills"""
    from accounts.models import UserProfile
    
    try:
        profile = UserProfile.objects.get(user=request.user)
        user_skills = [s.strip().lower() for s in profile.skills.split(',') if s.strip()]
    except UserProfile.DoesNotExist:
        user_skills = []
    
    if not user_skills:
        messages.info(request, 'Add skills to your profile to get personalized job recommendations.')
        return render(request, 'internships/recommended_jobs.html', {
            'jobs': [],
            'user_skills': []
        })
    
    jobs = Job.objects.filter(status='open')
    
    recommendations = []
    for job in jobs:
        job_skills = [s.strip().lower() for s in job.required_skills.split(',') if s.strip()]
        matching_skills = set(user_skills) & set(job_skills)
        
        if matching_skills:
            match_percentage = int((len(matching_skills) / len(job_skills)) * 100) if job_skills else 0
            recommendations.append({
                'job': job,
                'matching_skills': list(matching_skills),
                'match_percentage': match_percentage
            })
    
    recommendations.sort(key=lambda x: x['match_percentage'], reverse=True)
    
    return render(request, 'internships/recommended_jobs.html', {
        'recommendations': recommendations[:20],
        'user_skills': user_skills
    })


# ==================== ANALYTICS VIEWS ====================

@company_required
def job_analytics(request, pk):
    """View analytics for a specific job"""
    job = get_object_or_404(Job, pk=pk, company=request.user)
    
    from django.db.models.functions import TruncDate
    from django.utils import timezone
    from datetime import timedelta
    
    views = JobView.objects.filter(job=job)
    total_views = views.count()
    unique_viewers = views.exclude(viewer=None).values('viewer').distinct().count()
    
    last_30_days = timezone.now() - timedelta(days=30)
    daily_views = views.filter(viewed_at__gte=last_30_days)\
        .annotate(date=TruncDate('viewed_at'))\
        .values('date')\
        .annotate(count=Count('id'))\
        .order_by('date')
    
    applications = job.job_applications.all()
    app_by_status = applications.values('status').annotate(count=Count('id'))
    
    return render(request, 'internships/job_analytics.html', {
        'job': job,
        'total_views': total_views,
        'unique_viewers': unique_viewers,
        'daily_views': list(daily_views),
        'applications': applications,
        'app_by_status': {item['status']: item['count'] for item in app_by_status},
        'total_applications': applications.count(),
    })


@company_required
def company_dashboard_analytics(request):
    """Company-wide analytics dashboard"""
    from django.db.models.functions import TruncDate
    from django.utils import timezone
    from datetime import timedelta
    
    jobs = Job.objects.filter(company=request.user)
    
    total_jobs = jobs.count()
    active_jobs = jobs.filter(status='open').count()
    total_applications = JobApplication.objects.filter(job__company=request.user).count()
    total_views = JobView.objects.filter(job__company=request.user).count()
    
    last_7_days = timezone.now() - timedelta(days=7)
    recent_applications = JobApplication.objects.filter(
        job__company=request.user,
        applied_at__gte=last_7_days
    ).count()
    
    top_jobs = jobs.annotate(
        view_count=Count('views'),
        app_count=Count('job_applications')
    ).order_by('-view_count')[:5]
    
    return render(request, 'internships/company_analytics.html', {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'total_views': total_views,
        'recent_applications': recent_applications,
        'top_jobs': top_jobs,
    })


# ==================== INTERVIEW SCHEDULING ====================

@company_required
def schedule_interview(request, pk):
    """Schedule an interview for a job application"""
    application = get_object_or_404(JobApplication, pk=pk)
    
    if application.job.company != request.user:
        raise PermissionDenied("You don't have permission to schedule this interview.")
    
    if request.method == 'POST':
        form = InterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.scheduled_by = request.user
            interview.save()
            
            application.status = 'interview'
            application.save()
            
            send_interview_scheduled_email(interview)
            notify_interview_scheduled(interview)
            
            messages.success(request, 'Interview scheduled successfully!')
            return redirect('internships:job_application_detail', pk=pk)
    else:
        form = InterviewForm()
    
    return render(request, 'internships/schedule_interview.html', {
        'form': form,
        'application': application
    })


@company_required
def update_interview(request, pk):
    """Update/reschedule an interview"""
    interview = get_object_or_404(Interview, pk=pk)
    
    if interview.application.job.company != request.user:
        raise PermissionDenied("You don't have permission to update this interview.")
    
    if request.method == 'POST':
        form = InterviewForm(request.POST, instance=interview)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.status = 'rescheduled'
            interview.save()
            
            send_interview_scheduled_email(interview)
            
            messages.success(request, 'Interview rescheduled successfully!')
            return redirect('internships:job_application_detail', pk=interview.application.pk)
    else:
        form = InterviewForm(instance=interview)
    
    return render(request, 'internships/update_interview.html', {
        'form': form,
        'interview': interview
    })


@company_required
def cancel_interview(request, pk):
    """Cancel an interview"""
    interview = get_object_or_404(Interview, pk=pk)
    
    if interview.application.job.company != request.user:
        raise PermissionDenied("You don't have permission to cancel this interview.")
    
    if request.method == 'POST':
        interview.status = 'cancelled'
        interview.save()
        messages.success(request, 'Interview cancelled.')
        return redirect('internships:job_application_detail', pk=interview.application.pk)
    
    return render(request, 'internships/cancel_interview.html', {
        'interview': interview
    })


@company_required
def complete_interview(request, pk):
    """Mark interview as completed with feedback"""
    interview = get_object_or_404(Interview, pk=pk)
    
    if interview.application.job.company != request.user:
        raise PermissionDenied("You don't have permission to update this interview.")
    
    if request.method == 'POST':
        interview.status = 'completed'
        interview.notes = request.POST.get('notes', interview.notes)
        interview.save()
        messages.success(request, 'Interview marked as completed.')
        return redirect('internships:job_application_detail', pk=interview.application.pk)
    
    return render(request, 'internships/complete_interview.html', {
        'interview': interview
    })


@user_required
def my_interviews(request):
    """List user's scheduled interviews"""
    interviews = Interview.objects.filter(
        application__applicant=request.user
    ).select_related('application', 'application__job').order_by('scheduled_at')
    
    return render(request, 'internships/my_interviews.html', {
        'interviews': interviews
    })


# ==================== ATS RANKED APPLICANTS ====================

@company_required
def ranked_applicants(request, pk):
    """View ranked applicants for a job based on ATS match score"""
    job = get_object_or_404(Job, pk=pk, company=request.user)

    from assessments.models import VerifiedBadge

    applications = job.job_applications.select_related(
        'applicant__user_profile'
    ).all()

    # Prefetch all badges for these applicants in one query
    applicant_ids = [app.applicant_id for app in applications]
    all_badges = VerifiedBadge.objects.filter(
        user_id__in=applicant_ids
    ).values_list('user_id', 'skill_name')
    badges_by_user = {}
    for user_id, skill_name in all_badges:
        badges_by_user.setdefault(user_id, set()).add(skill_name.lower())

    job_skills = set(s.strip().lower() for s in job.required_skills.split(',') if s.strip())

    ranked = []
    for app in applications:
        try:
            profile = app.applicant.user_profile
        except Exception:
            profile = None

        # Skill match score (50% weight)
        if profile and profile.skills:
            user_skills = set(s.strip().lower() for s in profile.skills.split(',') if s.strip())
            matching = job_skills & user_skills
            missing = job_skills - user_skills
            skill_match = (len(matching) / len(job_skills) * 100) if job_skills else 0
        else:
            matching = set()
            missing = job_skills
            skill_match = 0

        # Experience score (20% weight)
        exp_map = {'fresher': 0, 'junior': 1, 'mid': 3, 'senior': 5, 'lead': 8}
        required_years = exp_map.get(job.experience_level, 0)
        actual_years = app.years_of_experience or 0
        if required_years > 0:
            experience_score = min(100, (actual_years / required_years) * 100)
        else:
            experience_score = 100 if actual_years > 0 else 50

        # Profile completeness (10% weight)
        profile_score = profile.completeness_score if profile else 0

        # Assessment score (20% weight) - check for verified badges
        badge_skills_lower = badges_by_user.get(app.applicant_id, set())
        verified_matching = job_skills & badge_skills_lower
        assessment_score = (len(verified_matching) / len(job_skills) * 100) if job_skills else 0

        # Final score
        final_score = (
            (skill_match * 0.5) +
            (experience_score * 0.2) +
            (profile_score * 0.1) +
            (assessment_score * 0.2)
        )

        ranked.append({
            'application': app,
            'profile': profile,
            'skill_match': round(skill_match, 1),
            'experience_score': round(experience_score, 1),
            'profile_score': round(profile_score, 1),
            'assessment_score': round(assessment_score, 1),
            'final_score': round(final_score, 1),
            'matching_skills': sorted(matching),
            'missing_skills': sorted(missing),
            'is_top': False,
        })

    ranked.sort(key=lambda x: x['final_score'], reverse=True)

    if ranked:
        ranked[0]['is_top'] = True

    return render(request, 'internships/ranked_applicants.html', {
        'job': job,
        'ranked_applicants': ranked,
        'total_applicants': len(ranked),
    })


# ==================== CSV EXPORT ====================

@company_required
def export_applications_csv(request, pk):
    """Export job applications as CSV for company download."""
    import csv
    from django.http import StreamingHttpResponse

    job = get_object_or_404(Job, pk=pk, company=request.user)
    applications = job.job_applications.select_related(
        'applicant__user_profile'
    ).order_by('-applied_at')

    class Echo:
        def write(self, value):
            return value

    def rows():
        writer = csv.writer(Echo())
        yield writer.writerow([
            'Name', 'Email', 'Phone', 'Status', 'Experience (years)',
            'Expected Salary', 'LinkedIn', 'Portfolio', 'Applied At',
        ])
        for app in applications:
            yield writer.writerow([
                app.full_name,
                app.email,
                app.phone,
                app.get_status_display(),
                app.years_of_experience,
                app.expected_salary or '',
                app.linkedin,
                app.portfolio,
                app.applied_at.strftime('%Y-%m-%d %H:%M'),
            ])

    response = StreamingHttpResponse(rows(), content_type='text/csv')
    filename = f'{job.title.replace(" ", "_")}_applications.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
