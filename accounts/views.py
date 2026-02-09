from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import UserRegisterForm, CompanyRegisterForm, UserProfileForm, CompanyProfileForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import CustomUser, PasswordResetOTP, UserProfile, CompanyProfile
import secrets
import logging

logger = logging.getLogger(__name__)


def send_otp_email(to_email, otp, user_type='user'):
    """Send OTP email using SendGrid"""
    
    # Always print OTP to console in DEBUG mode for testing
    if settings.DEBUG:
        print(f"\n{'='*50}")
        print(f"[OTP] Code for {to_email}: {otp}")
        print(f"{'='*50}\n")
        # In DEBUG mode, always return True so the flow continues
        # The OTP is printed above, so you can use it for testing
        return True
    
    # Production: Try to send via SendGrid
    if not settings.SENDGRID_API_KEY:
        logger.error("SENDGRID_API_KEY is not set")
        return False
    
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
    except ImportError:
        logger.error("SendGrid not installed. Run: pip install sendgrid")
        return False
    
    subject = 'Password Reset OTP - Remotely'
    
    if user_type == 'company':
        greeting = "Dear Company Admin"
    else:
        greeting = "Dear User"
    
    html_content = f'''
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #4F46E5;">Remotely - Password Reset</h2>
        <p>{greeting},</p>
        <p>You have requested to reset your password. Use the OTP below to proceed:</p>
        <div style="background-color: #F3F4F6; padding: 20px; text-align: center; margin: 20px 0;">
            <h1 style="color: #4F46E5; letter-spacing: 5px; margin: 0;">{otp}</h1>
        </div>
        <p><strong>This OTP is valid for 5 minutes.</strong></p>
        <p>If you didn't request this, please ignore this email.</p>
        <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 20px 0;">
        <p style="color: #6B7280; font-size: 12px;">This is an automated message from Remotely. Please do not reply.</p>
    </div>
    '''
    
    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"[SendGrid] Status: {response.status_code}")
        if response.status_code == 202:
            logger.info(f"OTP email sent successfully to {to_email}")
            return True
        else:
            logger.error(f"SendGrid returned status code: {response.status_code}")
            print(f"[SendGrid] Response body: {response.body}")
            return False
    except Exception as e:
        logger.error(f"SendGrid Error: {str(e)}")
        print(f"[SendGrid] Error: {str(e)}")
        return False

def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    user_form = UserRegisterForm()
    company_form = CompanyRegisterForm()
    
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        
        if user_type == 'user':
            user_form = UserRegisterForm(request.POST)
            if user_form.is_valid():
                user_form.save()
                return redirect('accounts:login_view')
        elif user_type == 'company':
            company_form = CompanyRegisterForm(request.POST)
            if company_form.is_valid():
                company_form.save()
                return redirect('accounts:login_view')
    
    return render(request, 'accounts/register.html', {
        'user_form': user_form,
        'company_form': company_form,
    })

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')

        user = authenticate(request, username=username, password=password)
        if user:
            if user.user_type == user_type:
                login(request, user)
                return redirect('accounts:dashboard')
            else:
                error = f"This account is not registered as a {user_type}."
        else:
            error = "Invalid username or password."

    return render(request, 'accounts/login.html', {'error': error})

@login_required
def dashboard(request):
    user = request.user
    profile = None
    context = {'user_type': user.user_type}
    
    if user.user_type == 'user':
        # USER/STUDENT DASHBOARD
        profile, _ = UserProfile.objects.get_or_create(user=user)
        
        # Import here to avoid circular imports
        from internships.models import Application, Internship, Job, JobApplication, JobBookmark, Interview
        
        # Get user's internship applications
        my_applications = Application.objects.filter(applicant=user).select_related(
            'internship', 'internship__company', 'internship__company__company_profile'
        ).order_by('-applied_at')
        
        # Get user's job applications
        my_job_applications = JobApplication.objects.filter(applicant=user).select_related(
            'job', 'job__company', 'job__company__company_profile'
        ).order_by('-applied_at')
        
        # Calculate stats
        total_applications = my_applications.count() + my_job_applications.count()
        pending_count = my_applications.filter(status='pending').count() + my_job_applications.filter(status='pending').count()
        accepted_count = my_applications.filter(status='accepted').count() + my_job_applications.filter(status='accepted').count()
        interview_count = my_job_applications.filter(status='interview').count()
        
        # Get available counts
        available_internships = Internship.objects.filter(status='open').count()
        available_jobs = Job.objects.filter(status='open').count()
        
        # Get saved jobs count
        saved_jobs_count = JobBookmark.objects.filter(user=user).count()
        
        # Get upcoming interviews
        upcoming_interviews = Interview.objects.filter(
            application__applicant=user,
            status='scheduled'
        ).select_related('application', 'application__job').order_by('scheduled_at')[:3]
        
        context.update({
            'profile': profile,
            'my_applications': my_applications[:5],
            'my_job_applications': my_job_applications[:5],
            'total_applications': total_applications,
            'pending_count': pending_count,
            'accepted_count': accepted_count,
            'interview_count': interview_count,
            'available_internships': available_internships,
            'available_jobs': available_jobs,
            'saved_jobs_count': saved_jobs_count,
            'upcoming_interviews': upcoming_interviews,
        })
        
    else:
        # COMPANY DASHBOARD
        profile, _ = CompanyProfile.objects.get_or_create(user=user)
        
        from internships.models import Internship, Application, Job, JobApplication, JobView
        from django.db.models import Count
        
        # Get company's internships with application counts
        my_internships = Internship.objects.filter(company=user).annotate(
            apps_count=Count('applications')
        ).order_by('-created_at')
        
        # Get company's jobs with application counts
        my_jobs = Job.objects.filter(company=user).annotate(
            apps_count=Count('job_applications')
        ).order_by('-created_at')
        
        # Calculate stats
        total_internship_posts = my_internships.count()
        total_job_posts = my_jobs.count()
        total_posts = total_internship_posts + total_job_posts
        active_posts = my_internships.filter(status='open').count() + my_jobs.filter(status='open').count()
        
        # Total applications across all postings
        internship_applications = Application.objects.filter(internship__company=user).count()
        job_applications = JobApplication.objects.filter(job__company=user).count()
        total_applications = internship_applications + job_applications
        
        pending_applications = Application.objects.filter(
            internship__company=user, status='pending'
        ).count() + JobApplication.objects.filter(
            job__company=user, status='pending'
        ).count()
        
        # Total views
        total_views = JobView.objects.filter(job__company=user).count()
        
        # Recent internship applications
        recent_internship_apps = Application.objects.filter(
            internship__company=user
        ).select_related('internship', 'applicant').order_by('-applied_at')[:3]
        
        # Recent job applications
        recent_job_apps = JobApplication.objects.filter(
            job__company=user
        ).select_related('job', 'applicant').order_by('-applied_at')[:3]
        
        context.update({
            'profile': profile,
            'my_internships': my_internships[:5],
            'my_jobs': my_jobs[:5],
            'total_posts': total_posts,
            'total_internship_posts': total_internship_posts,
            'total_job_posts': total_job_posts,
            'active_posts': active_posts,
            'total_applications': total_applications,
            'pending_applications': pending_applications,
            'total_views': total_views,
            'recent_internship_apps': recent_internship_apps,
            'recent_job_apps': recent_job_apps,
        })
    
    return render(request, 'accounts/dashboard.html', context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login_view')

def forgot_password(request):
    error = None
    success = None
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        
        if not email:
            error = "Please enter your email address."
        else:
            try:
                user = CustomUser.objects.get(email__iexact=email)
                otp = f"{secrets.randbelow(1000000):06d}"
                
                PasswordResetOTP.create_otp(user, otp)
                request.session['reset_email'] = email
                
                if send_otp_email(email, otp, user.user_type):
                    return redirect('accounts:otp_confirmation')
                else:
                    if not settings.SENDGRID_API_KEY:
                        error = "Email service not configured. Please contact support."
                    else:
                        error = "Failed to send OTP. Please try again later."
            except CustomUser.DoesNotExist:
                error = "No account found with this email address."
    
    return render(request, 'accounts/forgot_password.html', {'error': error, 'success': success})

def otp_confirmation(request):
    error = None
    
    if 'reset_email' not in request.session:
        return redirect('accounts:forgot_password')
    
    email = request.session.get('reset_email')
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        
        try:
            user = CustomUser.objects.get(email=email)
            otp_record = PasswordResetOTP.objects.filter(user=user, is_used=False).latest('created_at')
            
            if otp_record.verify_otp(entered_otp):
                request.session['otp_verified'] = True
                request.session['otp_id'] = otp_record.id
                return redirect('accounts:change_password')
            else:
                error = "Invalid or expired OTP. Please try again."
        except (CustomUser.DoesNotExist, PasswordResetOTP.DoesNotExist):
            error = "Invalid OTP. Please request a new one."
    
    return render(request, 'accounts/otp_confirmation.html', {'error': error, 'email': email})

def change_password(request):
    error = None
    
    if not request.session.get('otp_verified'):
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            error = "Passwords do not match."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."
        else:
            email = request.session.get('reset_email')
            otp_id = request.session.get('otp_id')
            
            try:
                user = CustomUser.objects.get(email=email)
                otp_record = PasswordResetOTP.objects.get(id=otp_id)
                
                otp_record.is_used = True
                otp_record.save()
                
                user.set_password(password)
                user.save()
                
                del request.session['reset_email']
                del request.session['otp_verified']
                del request.session['otp_id']
                
                return redirect('accounts:login_view')
            except (CustomUser.DoesNotExist, PasswordResetOTP.DoesNotExist):
                error = "Something went wrong. Please try again."
    
    return render(request, 'accounts/change_password.html', {'error': error})


@login_required
def edit_profile(request):
    user = request.user
    
    # Get or create the appropriate profile based on user type
    if user.user_type == 'user':
        profile, created = UserProfile.objects.get_or_create(user=user)
        FormClass = UserProfileForm
    else:
        profile, created = CompanyProfile.objects.get_or_create(user=user)
        FormClass = CompanyProfileForm
    
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save()
            profile.calculate_completeness()
            profile.save(update_fields=['completeness_score'])
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:dashboard')
    else:
        form = FormClass(instance=profile)
    
    return render(request, 'accounts/edit_profile.html', {
        'form': form,
        'profile': profile,
        'user_type': user.user_type
    })


def public_user_profile(request, username):
    """Public profile page for job seekers"""
    from .models import UserProfile
    target_user = get_object_or_404(CustomUser, username=username, user_type='user')
    profile = get_object_or_404(UserProfile, user=target_user)
    
    if not profile.is_public and (not request.user.is_authenticated or (request.user != target_user and not request.user.is_staff)):
        raise Http404
    
    is_owner = request.user.is_authenticated and request.user == target_user
    
    experiences = profile.experiences.all()
    educations = profile.educations.all()
    projects = profile.projects.all()
    
    skills_list = [s.strip() for s in profile.skills.split(',') if s.strip()] if profile.skills else []
    
    return render(request, 'accounts/public_user_profile.html', {
        'target_user': target_user,
        'profile': profile,
        'is_owner': is_owner,
        'experiences': experiences,
        'educations': educations,
        'projects': projects,
        'skills_list': skills_list,
    })


def public_company_profile(request, slug):
    """Public profile page for companies"""
    from .models import CompanyProfile
    from internships.models import Job, Internship
    
    profile = get_object_or_404(CompanyProfile, slug=slug)
    
    if not profile.is_public and (not request.user.is_authenticated or (request.user != profile.user and not request.user.is_staff)):
        raise Http404
    
    is_owner = request.user.is_authenticated and request.user == profile.user
    
    open_jobs = Job.objects.filter(company=profile.user, status='open').order_by('-created_at')[:10]
    open_internships = Internship.objects.filter(company=profile.user, status='open').order_by('-created_at')[:10]
    
    total_jobs = Job.objects.filter(company=profile.user).count()
    total_internships = Internship.objects.filter(company=profile.user).count()
    
    return render(request, 'accounts/public_company_profile.html', {
        'profile': profile,
        'target_user': profile.user,
        'is_owner': is_owner,
        'open_jobs': open_jobs,
        'open_internships': open_internships,
        'total_jobs': total_jobs,
        'total_internships': total_internships,
    })


@login_required
def company_approval_status(request):
    """Shows company approval status, rejection reason, and guidance"""
    if request.user.user_type != 'company':
        return redirect('accounts:dashboard')
    
    profile, _ = CompanyProfile.objects.get_or_create(user=request.user)
    profile.calculate_completeness()
    profile.save(update_fields=['completeness_score'])
    
    return render(request, 'accounts/company_approval_status.html', {
        'profile': profile,
        'user_type': 'company',
    })
