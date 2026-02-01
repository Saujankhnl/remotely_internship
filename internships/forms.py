from django import forms
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from .models import Internship, Application

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


class InternshipForm(forms.ModelForm):
    """Form for creating/editing internships"""
    
    class Meta:
        model = Internship
        fields = [
            'title', 'description', 'internship_type', 'required_skills',
            'qualifications', 'experience', 'location', 'email', 
            'salary', 'duration'
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
