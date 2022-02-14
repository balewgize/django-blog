from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.signin, name="login"),
    path("logout/", views.signout, name="logout"),
    path("verify/", views.inform_to_verify, name="verify"),
    path("bookmark/", views.BookmarkPost.as_view(), name="bookmark"),
    path("confirm/<uidb64>/<token>/", views.activate, name="activate"),
    path("<str:uid>/", views.UserProfileView.as_view(), name="profile"),
    path("<str:uid>/update/", views.update_profile, name="update-profile"),
    path("<str:uid>/draft/", views.DraftPostView.as_view(), name="draft"),
    path("<str:uid>/saved/", views.SavedPostView.as_view(), name="saved"),
]
