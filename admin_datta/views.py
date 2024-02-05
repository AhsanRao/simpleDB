from django.shortcuts import render, redirect
from admin_datta.forms import (
    RegistrationForm,
    LoginForm,
    UserPasswordChangeForm,
    UserPasswordResetForm,
    UserSetPasswordForm,
    OwnerRegistrationForm,
    StaffRegistrationForm,
)
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.views.generic import CreateView
from django.contrib.auth import logout

from django.contrib.auth.decorators import login_required


@login_required(login_url="/accounts/login/")
def index(request):
    context = {"segment": "index"}
    return render(request, "pages/index.html", context)


@login_required(login_url="/accounts/login/")
def generate_report(request):
    context = {"segment": "generate-report"}
    return render(request, "pages/chart-morris.html", context)


class OwnerRegistrationView(CreateView):
    template_name = "accounts/auth-signup.html"
    form_class = OwnerRegistrationForm
    success_url = "/accounts/login/"


class StaffRegistrationView(CreateView):
    template_name = "accounts/auth-signup.html"
    form_class = StaffRegistrationForm
    success_url = "/accounts/login/"


def register(request):
    return render(request, "accounts/auth-register.html")


# Authentication
class UserRegistrationView(CreateView):
    template_name = "accounts/auth-register.html"
    form_class = RegistrationForm
    success_url = "/accounts/login/"


class UserLoginView(LoginView):
    template_name = "accounts/auth-signin.html"
    form_class = LoginForm


class UserPasswordResetView(PasswordResetView):
    template_name = "accounts/auth-reset-password.html"
    form_class = UserPasswordResetForm


class UserPasswrodResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/auth-password-reset-confirm.html"
    form_class = UserSetPasswordForm


class UserPasswordChangeView(PasswordChangeView):
    template_name = "accounts/auth-change-password.html"
    form_class = UserPasswordChangeForm


def logout_view(request):
    logout(request)
    return redirect("/accounts/login/")
