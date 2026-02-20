from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path("", views.register, name="register"),
    path("login/", views.login_view, name="login_view"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path("change-password/", views.change_password, name="change_password"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("otp-confirmation/", views.otp_confirmation, name="otp_confirmation"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),

    # Public profile pages
    path("u/<str:username>/", views.public_user_profile, name="public_user_profile"),
    path("c/<slug:slug>/", views.public_company_profile, name="public_company_profile"),

    # Company approval
    path("company/approval/", views.company_approval_status, name="company_approval_status"),

    # Admin dashboard
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
]