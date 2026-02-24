from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .signals import create_profile_for_user


@login_required
def select_role(request):
    """Role selection page after social login"""
    user = request.user

    # If user already has a type, redirect to dashboard
    if user.user_type:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        role = request.POST.get('role')
        if role in ('user', 'company'):
            user.user_type = role
            user.save(update_fields=['user_type'])
            create_profile_for_user(user)
            messages.success(
                request,
                f'Account setup complete! You are now registered as a '
                f'{"Job Seeker" if role == "user" else "Company"}.'
            )
            return redirect('accounts:dashboard')

    return render(request, 'accounts/select_role.html', {})
