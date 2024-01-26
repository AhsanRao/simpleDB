from django.urls import path
from admin_datta import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("", views.index, name="index"),
    # Chart and Maps
    path("charts/morris-chart/", views.morris_chart, name="morris_chart"),
    path("maps/google-maps/", views.google_maps, name="google_maps"),
    path("report", views.generate_report, name="generate_report"),
    # Authentication
    path("accounts/register/", views.register, name="register"),
    path(
        "accounts/register/owner/",
        views.OwnerRegistrationView.as_view(),
        name="register-owner",
    ),
    path(
        "accounts/register/staff/",
        views.StaffRegistrationView.as_view(),
        name="register-staff",
    ),
    path("accounts/login/", views.UserLoginView.as_view(), name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
    path(
        "accounts/password-change/",
        views.UserPasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "accounts/password-change-done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="accounts/auth-password-change-done.html"
        ),
        name="password_change_done",
    ),
    path(
        "accounts/password-reset/",
        views.UserPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "accounts/password-reset-confirm/<uidb64>/<token>/",
        views.UserPasswrodResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "accounts/password-reset-done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/auth-password-reset-done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "accounts/password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/auth-password-reset-complete.html"
        ),
        name="password_reset_complete",
    ),
    #
    path("profile/", views.profile, name="profile"),
    path("sample-page/", views.sample_page, name="sample_page"),
]
