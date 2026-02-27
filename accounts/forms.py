from django import forms
from .models import CustomUser, UserProfile, CompanyProfile, UserExperience, UserEducation, UserProject

INPUT_CLASS = 'w-full px-4 py-3 text-base border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
DARK_INPUT_CLASS = 'w-full px-4 py-3 text-base bg-gray-700 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'


class UserRegisterForm(forms.ModelForm):
    """Registration form for Users (Job Seekers)"""
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': INPUT_CLASS,
        'placeholder': 'Enter password'
    }))
    full_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': INPUT_CLASS,
        'placeholder': 'Enter your full name'
    }))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Enter username'
            }),
            'email': forms.EmailInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Enter email'
            }),
        }
        help_texts = {
            'username': '',
            'email': '',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.user_type = 'user'
        if commit:
            user.save()
            # Create UserProfile
            UserProfile.objects.create(
                user=user,
                full_name=self.cleaned_data.get('full_name', '')
            )
        return user


class CompanyRegisterForm(forms.ModelForm):
    """Registration form for Companies"""
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': INPUT_CLASS,
        'placeholder': 'Enter password'
    }))
    company_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': INPUT_CLASS,
        'placeholder': 'Enter company name'
    }))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Enter username'
            }),
            'email': forms.EmailInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Enter company email'
            }),
        }
        help_texts = {
            'username': '',
            'email': '',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.user_type = 'company'
        if commit:
            user.save()
            # Create CompanyProfile
            CompanyProfile.objects.create(
                user=user,
                company_name=self.cleaned_data.get('company_name', '')
            )
        return user


class UserProfileForm(forms.ModelForm):
    """Profile edit form for Users"""
    class Meta:
        model = UserProfile
        fields = ['profile_photo', 'full_name', 'headline', 'phone', 'location', 'bio', 
                  'skills', 'education', 'experience', 'course', 'gpa',
                  'english_level', 'internet_quality', 'available_hours',
                  'open_to_work', 'is_public',
                  'linkedin', 'github', 'facebook', 'instagram', 'whatsapp']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Your full name'
            }),
            'headline': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., CS Student | Frontend Developer'
            }),
            'phone': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': '+91 9876543210'
            }),
            'location': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'City, Country'
            }),
            'bio': forms.Textarea(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Tell us about yourself...',
                'rows': 4
            }),
            'skills': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Python, JavaScript, React, Django'
            }),
            'education': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'B.Tech in Computer Science'
            }),
            'experience': forms.Textarea(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Your work experience...',
                'rows': 3
            }),
            'course': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., Computer Science, BBA, MBA'
            }),
            'gpa': forms.NumberInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., 3.5',
                'step': '0.01',
                'min': '0',
                'max': '4'
            }),
            'english_level': forms.Select(attrs={
                'class': DARK_INPUT_CLASS,
            }),
            'internet_quality': forms.Select(attrs={
                'class': DARK_INPUT_CLASS,
            }),
            'available_hours': forms.NumberInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Weekly hours available',
                'min': '0',
                'max': '168'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'https://linkedin.com/in/username'
            }),
            'github': forms.URLInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'https://github.com/username'
            }),
            'facebook': forms.URLInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'https://facebook.com/username'
            }),
            'instagram': forms.URLInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'https://instagram.com/username'
            }),
            'whatsapp': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': '+91 9876543210'
            }),
            'open_to_work': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 rounded',
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 rounded',
            }),
            'profile_photo': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*'
            }),
        }


class CompanyProfileForm(forms.ModelForm):
    """Profile edit form for Companies"""
    class Meta:
        model = CompanyProfile
        fields = ['logo', 'company_name', 'phone', 'location', 'bio',
                  'industry', 'company_size', 'founded_year', 'website',
                  'is_public', 'linkedin', 'facebook', 'instagram', 'whatsapp']
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Company name'
            }),
            'phone': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': '+91 9876543210'
            }),
            'location': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'City, Country'
            }),
            'bio': forms.Textarea(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Tell us about your company...',
                'rows': 4
            }),
            'industry': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., Technology, Healthcare'
            }),
            'company_size': forms.Select(attrs={
                'class': DARK_INPUT_CLASS,
            }, choices=[
                ('', 'Select company size'),
                ('1-10', '1-10 employees'),
                ('11-50', '11-50 employees'),
                ('51-200', '51-200 employees'),
                ('201-500', '201-500 employees'),
                ('500+', '500+ employees'),
            ]),
            'founded_year': forms.NumberInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': '2020'
            }),
            'website': forms.URLInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'https://yourcompany.com'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'https://linkedin.com/company/yourcompany'
            }),
            'facebook': forms.URLInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'https://facebook.com/yourcompany'
            }),
            'instagram': forms.URLInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'https://instagram.com/yourcompany'
            }),
            'whatsapp': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': '+91 9876543210'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 rounded',
            }),
        }


class UserExperienceForm(forms.ModelForm):
    class Meta:
        model = UserExperience
        fields = ['title', 'company_name', 'location', 'employment_type',
                  'start_date', 'end_date', 'is_current', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., Software Engineer'
            }),
            'company_name': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., Google'
            }),
            'location': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., New York, USA'
            }),
            'employment_type': forms.Select(attrs={
                'class': DARK_INPUT_CLASS,
            }),
            'start_date': forms.DateInput(attrs={
                'class': DARK_INPUT_CLASS,
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': DARK_INPUT_CLASS,
                'type': 'date'
            }),
            'is_current': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 rounded',
            }),
            'description': forms.Textarea(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'What did you do in this role?',
                'rows': 3,
            }),
        }


class UserEducationForm(forms.ModelForm):
    class Meta:
        model = UserEducation
        fields = ['school', 'degree', 'field_of_study', 'start_year', 'end_year', 'description']
        widgets = {
            'school': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., MIT'
            }),
            'degree': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., Bachelor of Science'
            }),
            'field_of_study': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., Computer Science'
            }),
            'start_year': forms.NumberInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': '2020'
            }),
            'end_year': forms.NumberInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': '2024'
            }),
            'description': forms.Textarea(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Activities, honors, etc.',
                'rows': 3,
            }),
        }


class UserProjectForm(forms.ModelForm):
    class Meta:
        model = UserProject
        fields = ['name', 'url', 'description', 'technologies', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'e.g., E-commerce Platform'
            }),
            'url': forms.URLInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'https://github.com/...'
            }),
            'description': forms.Textarea(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'What does this project do?',
                'rows': 3,
            }),
            'technologies': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Python, Django, React'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 rounded',
            }),
        }
