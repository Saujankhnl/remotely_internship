from django import forms
from .models import CustomUser, UserProfile, CompanyProfile

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
        fields = ['profile_photo', 'full_name', 'phone', 'location', 'bio', 
                  'skills', 'education', 'experience', 'linkedin', 'github', 
                  'facebook', 'instagram', 'whatsapp']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': DARK_INPUT_CLASS,
                'placeholder': 'Your full name'
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
                  'linkedin', 'facebook', 'instagram', 'whatsapp']
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
        }
