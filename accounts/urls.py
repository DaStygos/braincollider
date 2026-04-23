from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from accounts.forms import PasswordChangeFormCustom
from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("profile/", views.profile, name="profile"),
    path("u/<str:username>/", views.public_profile, name="public_profile"),
    path("users/", views.user_search, name="user_search"),
    path("users/suggest/", views.matching_users, name="user_suggestions"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
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
        auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"),
        name="password_reset",
    ),
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name="accounts/logged_out.html"), name="logout"),
]
