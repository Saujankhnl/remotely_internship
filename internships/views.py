from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, Http404
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from functools import wraps
from .models import Internship, Application
from .forms import InternshipForm, ApplicationForm


def company_required(view_func):
    """Decorator to ensure only companies can access the view"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login_view')
        if request.user.user_type != 'company':
            raise PermissionDenied("Only companies can access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper


def user_required(view_func):
    """Decorator to ensure only users can access the view"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login_view')
        if request.user.user_type != 'user':
            raise PermissionDenied("Only users can access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper


# ============ Public Views ============

def internship_list(request):
    """List all open internships with search/filter"""
    internships = Internship.objects.filter(status='open')
    
    # Search
    query = request.GET.get('q', '')
    if query:
        internships = internships.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(required_skills__icontains=query) |
            Q(location__icontains=query)
        )
    
    # Filter by type
    internship_type = request.GET.get('type', '')
    if internship_type in ['paid', 'unpaid']:
        internships = internships.filter(internship_type=internship_type)
    
    # Filter by location
    location = request.GET.get('location', '')
    if location:
        internships = internships.filter(location__icontains=location)
    
    return render(request, 'internships/internship_list.html', {
        'internships': internships,
        'query': query,
        'selected_type': internship_type,
        'selected_location': location,
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

@company_required
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


@company_required
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
    """List company's own internships with application counts"""
    internships = Internship.objects.filter(company=request.user)
    
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
    
    return render(request, 'internships/view_applications.html', {
        'internship': internship,
        'applications': applications,
        'selected_status': status,
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
            application.status = new_status
            application.save()
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
