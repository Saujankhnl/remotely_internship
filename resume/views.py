from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from django.core.files.base import ContentFile
from django.views.decorators.http import require_POST

from accounts.models import UserProfile, UserExperience, UserEducation, UserProject
from accounts.decorators import user_required
from .models import GeneratedResume
from .pdf_generator import TEMPLATE_GENERATORS


def _get_user_data(user):
    """Helper to fetch all user profile data for resume generation."""
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = None

    experiences = []
    educations = []
    projects = []

    if profile:
        experiences = list(profile.experiences.all())
        educations = list(profile.educations.all())
        projects = list(profile.projects.all())

    return profile, experiences, educations, projects


@user_required
def resume_builder(request):
    """Shows resume preview page with template selection."""
    profile, experiences, educations, projects = _get_user_data(request.user)

    profile_complete = profile is not None and profile.completeness_score >= 50

    return render(request, 'resume/resume_builder.html', {
        'profile': profile,
        'experiences': experiences,
        'educations': educations,
        'projects': projects,
        'profile_complete': profile_complete,
    })


@user_required
@require_POST
def generate_resume_pdf(request):
    """Generate and download a PDF resume."""
    template_name = request.POST.get('template_name', 'professional')

    if template_name not in TEMPLATE_GENERATORS:
        messages.error(request, 'Invalid template selected.')
        return redirect('resume:resume_builder')

    profile, experiences, educations, projects = _get_user_data(request.user)

    if not profile:
        messages.error(request, 'Please complete your profile before generating a resume.')
        return redirect('accounts:edit_profile')

    generator = TEMPLATE_GENERATORS[template_name]
    pdf_buffer = generator(profile, experiences, educations, projects, request.user)

    # Save record
    resume_record = GeneratedResume(user=request.user, template_name=template_name)
    filename = f"resume_{request.user.username}_{template_name}.pdf"
    resume_record.file.save(filename, ContentFile(pdf_buffer.read()), save=True)

    # Re-read buffer for response
    pdf_buffer.seek(0)

    response = FileResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@user_required
def resume_preview(request, template_name):
    """HTML preview of resume with selected template."""
    if template_name not in TEMPLATE_GENERATORS:
        raise Http404("Template not found.")

    profile, experiences, educations, projects = _get_user_data(request.user)

    return render(request, 'resume/resume_preview.html', {
        'profile': profile,
        'experiences': experiences,
        'educations': educations,
        'projects': projects,
        'user': request.user,
        'template_name': template_name,
    })


@user_required
def my_resumes(request):
    """List of previously generated resumes."""
    resumes = GeneratedResume.objects.filter(user=request.user)

    return render(request, 'resume/my_resumes.html', {
        'resumes': resumes,
    })


@user_required
@require_POST
def delete_resume(request, pk):
    """Delete a generated resume."""
    resume = get_object_or_404(GeneratedResume, pk=pk, user=request.user)
    if resume.file:
        resume.file.delete(save=False)
    resume.delete()
    messages.success(request, 'Resume deleted successfully.')
    return redirect('resume:my_resumes')
