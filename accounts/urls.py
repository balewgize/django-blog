from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("verify/", views.inform_to_verify, name="verify"),
    path("confirm/<uidb64>/<token>/", views.activate, name="activate"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="blog:post-list"),
        name="logout",
    ),
    path("<str:slug>/", views.UserProfileView.as_view(), name="profile"),
]
