from django.urls import path

from . import views


app_name = "blog"

urlpatterns = [
    path("", views.HomePage.as_view(), name="home"),
    path("stories/", views.PostList.as_view(), name="post-list"),
    path("p/new/", views.PostCreate.as_view(), name="post-create"),
    path("p/<slug:slug>/", views.PostDetail.as_view(), name="post-detail"),
    path("p/<slug:slug>/edit/", views.PostUpdate.as_view(), name="post-update"),
    path("p/<slug:slug>/delete/", views.PostDelete.as_view(), name="post-delete"),
    path("p/<slug:slug>/comments/", views.comments, name="comment-list"),
    path(
        "p/<slug:slug>/comments/<int:pk>/edit/",
        views.CommentUpdate.as_view(),
        name="comment-update",
    ),
    path(
        "p/<slug:slug>/comments/<int:pk>/delete/",
        views.CommentDelete.as_view(),
        name="comment-delete",
    ),
    path("category/<slug:slug>/", views.CategoryView.as_view(), name="category"),
]
