from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        if user.is_authenticated and not user.user_type:
            return '/select-role/'
        return '/dashboard/'


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """Link social account to existing user with same email"""
        if sociallogin.is_existing:
            return

        email = sociallogin.account.extra_data.get('email') or ''
        if not email:
            try:
                email = sociallogin.email_addresses[0].email
            except (IndexError, AttributeError):
                return

        from accounts.models import CustomUser
        try:
            existing_user = CustomUser.objects.get(email=email)
            sociallogin.connect(request, existing_user)
        except CustomUser.DoesNotExist:
            pass

    def get_login_redirect_url(self, request):
        user = request.user
        if user.is_authenticated and not user.user_type:
            return '/select-role/'
        return '/dashboard/'

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        data = sociallogin.account.extra_data
        if not user.first_name:
            user.first_name = data.get('given_name', data.get('firstName', ''))
        if not user.last_name:
            user.last_name = data.get('family_name', data.get('lastName', ''))
        user.save()
        return user
