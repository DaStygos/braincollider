from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator
from core.rate_limits import rate_limit

from accounts.forms import PasswordChangeFormCustom
from . import views

app_name = "accounts"


@method_decorator(rate_limit("login", limit=30, period=15 * 60, methods={"POST"}), name="dispatch")
class RateLimitedLoginView(LoginView):
    template_name = "accounts/login.html"


@method_decorator(rate_limit("password-reset", limit=5, period=60 * 60, methods={"POST"}), name="dispatch")
class RateLimitedPasswordResetView(auth_views.PasswordResetView):
    template_name = "accounts/password_reset.html"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("profile/", views.profile, name="profile"),
    path("u/<str:username>/", views.public_profile, name="public_profile"),
    path("users/", views.user_search, name="user_search"),
    path("users/suggest/", views.matching_users, name="user_suggestions"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("delete/", views.delete_account, name="delete_account"),
    path(
        "password/change/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/password_change.html",
            success_url=reverse_lazy("accounts:password_change_done"),
            form_class=PasswordChangeFormCustom,
        ),
        name="password_change",
    ),
    path(
        "password/change/done/",
        auth_views.PasswordChangeDoneView.as_view(template_name="accounts/password_change_done.html"),
        name="password_change_done",
    ),
    path(
        "password/reset/",
        RateLimitedPasswordResetView.as_view(),
        name="password_reset",
    ),
    path("login/", RateLimitedLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name="accounts/logged_out.html"), name="logout"),
]
