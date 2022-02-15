from unicodedata import name
from django.urls import path

from . import views


app_name = "blog"

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("stories/", views.PostListView.as_view(), name="post-list"),
    path("p/new/", views.PostCreateView.as_view(), name="post-create"),
    path("p/<slug:slug>/", views.PostDetailView.as_view(), name="post-detail"),
    path("p/<slug:slug>/edit/", views.PostUpdateView.as_view(), name="post-update"),
    path("p/<slug:slug>/delete/", views.PostDeleteView.as_view(), name="post-delete"),
    path("category/<slug:slug>/", views.CategoryView.as_view(), name="category"),
]
