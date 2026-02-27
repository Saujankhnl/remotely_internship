from django import forms
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from .models import (
    Internship, Application, Job, JobApplication, Interview,
    ApplicationRemark, RejectionTag, AcceptanceTag, CandidateFeedback,
)

DARK_INPUT_CLASS = 'w-full px-4 py-3 text-base bg-gray-700 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'

# Maximum file size: 5MB
MAX_CV_SIZE = 5 * 1024 * 1024  # 5MB in bytes
ALLOWED_CV_EXTENSIONS = ['pdf', 'doc', 'docx']


def validate_cv_file(file):
    """Validate CV file type and size"""
    if file.size > MAX_CV_SIZE:
        raise ValidationError(f'File size must be under 5MB. Your file is {file.size / (1024*1024):.1f}MB.')
    
    # Check file extension
    ext = file.name.split('.')[-1].lower()
    if ext not in ALLOWED_CV_EXTENSIONS:
        raise ValidationError(f'Only PDF, DOC, DOCX files allowed. You uploaded a .{ext} file.')


# ==================== JOB FORMS ====================

class JobForm(forms.ModelForm):
    """Form for creating/editing jobs"""
    
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'job_type', 'required_skills',
            'qualifications', 'experience_level', 'salary_min', 'salary_max',
            'salary_currency', 'location', 'is_remote', 'email', 
            'benefits', 'deadline',
            'is_premium', 'auto_screen_enabled', 'required_course',
            'min_gpa', 'preferred_english_level', 'preferred_internet_quality',
            'preferred_location'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., Senior Software Engineer'
            }),
            'description': forms.Textarea(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Describe the job role, responsibilities...',
                'rows': 5
            }),
            'job_type': forms.Select(attrs={
                'class': DARK_INPUT_CLASS,
            }),
            'required_skills': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Python, Django, PostgreSQL, AWS'
            }),
            'qualifications': forms.Textarea(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Required qualifications...',
                'rows': 3
            }),
            'experience_level': forms.Select(attrs={
                'class': DARK_INPUT_CLASS,
            }),
            'salary_min': forms.NumberInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., 50000'
            }),
            'salary_max': forms.NumberInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., 80000'
            }),
            'salary_currency': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'USD'
            }),
            'location': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., New York, USA'
            }),
            'is_remote': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 rounded'
            }),
            'email': forms.EmailInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'hr@company.com'
            }),
            'benefits': forms.Textarea(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Health insurance, 401k, Remote work...',
                'rows': 3
            }),
            'deadline': forms.DateInput(attrs={
                'class': DARK_INPUT_CLASS,
                'type': 'date'
            }),
            'is_premium': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 rounded'
            }),
            'auto_screen_enabled': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 rounded'
            }),
            'required_course': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., Computer Science, BBA'
            }),
            'min_gpa': forms.NumberInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., 3.0',
                'step': '0.01',
                'min': '0',
                'max': '4'
            }),
            'preferred_english_level': forms.Select(attrs={
                'class': DARK_INPUT_CLASS,
            }),
            'preferred_internet_quality': forms.Select(attrs={
                'class': DARK_INPUT_CLASS,
            }, choices=[('', 'Any'), ('poor', 'Poor'), ('average', 'Average'), ('good', 'Good'), ('excellent', 'Excellent')]),
            'preferred_location': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Preferred candidate location'
            }),
        }


class JobApplicationForm(forms.ModelForm):
    """Form for applying to jobs"""
    
    class Meta:
        model = JobApplication
        fields = [
            'full_name', 'email', 'phone', 'cover_letter', 
            'cv', 'expected_salary', 'years_of_experience',
            'notice_period', 'linkedin', 'portfolio'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'your.email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': '+1 234 567 8900'
            }),
            'cover_letter': forms.Textarea(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Why are you the right fit for this role?',
                'rows': 5
            }),
            'cv': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': '.pdf,.doc,.docx'
            }),
            'expected_salary': forms.NumberInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Expected annual salary'
            }),
            'years_of_experience': forms.NumberInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Years of experience'
            }),
            'notice_period': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., 2 weeks, 1 month'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'https://linkedin.com/in/yourprofile'
            }),
            'portfolio': forms.URLInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'https://yourportfolio.com'
            }),
        }
    
    def clean_cv(self):
        """Validate CV file"""
        cv = self.cleaned_data.get('cv')
        if cv:
            validate_cv_file(cv)
        return cv


# ==================== INTERNSHIP FORMS ====================


class InternshipForm(forms.ModelForm):
    """Form for creating/editing internships"""
    
    class Meta:
        model = Internship
        fields = [
            'title', 'description', 'internship_type', 'required_skills',
            'qualifications', 'experience', 'location', 'email', 
            'salary', 'duration', 'deadline',
            'is_premium', 'auto_screen_enabled', 'required_course',
            'min_gpa', 'preferred_english_level', 'preferred_internet_quality',
            'preferred_location'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., Frontend Developer Intern'
            }),
            'description': forms.Textarea(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Describe the internship role, responsibilities, and what the intern will learn...',
                'rows': 5
            }),
            'internship_type': forms.Select(attrs={
                'class': DARK_INPUT_CLASS,
            }),
            'required_skills': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Python, Django, JavaScript, React'
            }),
            'qualifications': forms.Textarea(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., Currently pursuing B.Tech in Computer Science...',
                'rows': 3
            }),
            'experience': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., 0-1 years (Required for paid internships)'
            }),
            'location': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., Remote, New York, Hybrid'
            }),
            'email': forms.EmailInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'hr@company.com'
            }),
            'salary': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., $500/month (for paid internships)'
            }),
            'duration': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., 3 months, 6 months'
            }),
            'deadline': forms.DateInput(attrs={
                'class': DARK_INPUT_CLASS,
                'type': 'date'
            }),
            'is_premium': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 rounded'
            }),
            'auto_screen_enabled': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 rounded'
            }),
            'required_course': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., Computer Science, BBA'
            }),
            'min_gpa': forms.NumberInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., 3.0',
                'step': '0.01',
                'min': '0',
                'max': '4'
            }),
            'preferred_english_level': forms.Select(attrs={
                'class': DARK_INPUT_CLASS,
            }),
            'preferred_internet_quality': forms.Select(attrs={
                'class': DARK_INPUT_CLASS,
            }, choices=[('', 'Any'), ('poor', 'Poor'), ('average', 'Average'), ('good', 'Good'), ('excellent', 'Excellent')]),
            'preferred_location': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Preferred candidate location'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        internship_type = cleaned_data.get('internship_type')
        experience = cleaned_data.get('experience')
        
        # Experience is mandatory for paid internships
        if internship_type == 'paid' and not experience:
            self.add_error('experience', 'Experience is required for paid internships.')
        
        return cleaned_data


class ApplicationForm(forms.ModelForm):
    """Form for applying to internships"""
    
    class Meta:
        model = Application
        fields = [
            'full_name', 'email', 'phone', 'cover_letter', 
            'cv', 'linkedin', 'portfolio'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'your.email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': '+1 234 567 8900'
            }),
            'cover_letter': forms.Textarea(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Tell us why you are interested in this internship and what makes you a great fit...',
                'rows': 5
            }),
            'cv': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': '.pdf,.doc,.docx'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'https://linkedin.com/in/yourprofile'
            }),
            'portfolio': forms.URLInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'https://yourportfolio.com'
            }),
        }
    
    def clean_cv(self):
        """Validate CV file"""
        cv = self.cleaned_data.get('cv')
        if cv:
            validate_cv_file(cv)
        return cv


class InterviewForm(forms.ModelForm):
    """Form for scheduling interviews"""
    
    class Meta:
        model = Interview
        fields = ['interview_type', 'scheduled_at', 'duration_minutes', 'location', 'notes']
        widgets = {
            'interview_type': forms.Select(attrs={
                'class': DARK_INPUT_CLASS,
            }),
            'scheduled_at': forms.DateTimeInput(attrs={
                'class': DARK_INPUT_CLASS,
                'type': 'datetime-local'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': '60',
                'min': '15',
                'max': '480'
            }),
            'location': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Meeting link or address'
            }),
            'notes': forms.Textarea(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Additional notes for the candidate...',
                'rows': 3
            }),
        }


class ApplicationRemarkForm(forms.ModelForm):
    """Form for adding structured remarks when changing application status"""
    
    class Meta:
        model = ApplicationRemark
        fields = ['remark_type', 'rejection_tags', 'acceptance_tags', 'custom_remarks', 'hr_notes']
        widgets = {
            'remark_type': forms.HiddenInput(),
            'rejection_tags': forms.CheckboxSelectMultiple(attrs={
                'class': 'space-y-2',
            }),
            'acceptance_tags': forms.CheckboxSelectMultiple(attrs={
                'class': 'space-y-2',
            }),
            'custom_remarks': forms.Textarea(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Additional remarks visible to candidate...',
                'rows': 3
            }),
            'hr_notes': forms.Textarea(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Internal HR notes (not visible to candidate)...',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rejection_tags'].queryset = RejectionTag.objects.filter(is_active=True)
        self.fields['acceptance_tags'].queryset = AcceptanceTag.objects.filter(is_active=True)
        self.fields['rejection_tags'].required = False
        self.fields['acceptance_tags'].required = False


class CandidateFeedbackForm(forms.ModelForm):
    """Form for sending feedback to candidates"""
    
    class Meta:
        model = CandidateFeedback
        fields = ['feedback_type', 'message', 'suggested_skills', 'is_visible']
        widgets = {
            'feedback_type': forms.Select(attrs={
                'class': DARK_INPUT_CLASS,
            }),
            'message': forms.Textarea(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Provide constructive feedback...',
                'rows': 4
            }),
            'suggested_skills': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Python, Django, React (comma separated)'
            }),
            'is_visible': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 rounded'
            }),
        }
