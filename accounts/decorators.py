from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from functools import wraps


def company_approved_required(view_func):
    """Decorator to ensure only approved companies can access the view.
    Use this for views that require company approval (e.g., creating jobs/internships).
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login_view')
        if request.user.user_type != 'company':
            raise PermissionDenied("Only companies can access this page.")

        from accounts.models import CompanyProfile
        profile, _ = CompanyProfile.objects.get_or_create(user=request.user)
        if profile.approval_status != 'approved':
            messages.warning(request, "Your company must be approved before you can post jobs or internships. Please complete your profile and wait for admin approval.")
            return redirect('accounts:company_approval_status')
        return view_func(request, *args, **kwargs)
    return wrapper
