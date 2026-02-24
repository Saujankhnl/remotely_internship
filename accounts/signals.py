from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from .models import UserProfile, CompanyProfile


@receiver(user_signed_up)
def handle_user_signed_up(request, user, **kwargs):
    """After social signup, redirect to role selection if no user_type set"""
    if not user.user_type:
        # Will be handled by role selection view
        pass


def create_profile_for_user(user):
    """Create appropriate profile based on user_type"""
    if user.user_type == 'user':
        UserProfile.objects.get_or_create(
            user=user,
            defaults={'full_name': user.get_full_name() or user.username}
        )
    elif user.user_type == 'company':
        CompanyProfile.objects.get_or_create(
            user=user,
            defaults={'company_name': user.get_full_name() or user.username}
        )
