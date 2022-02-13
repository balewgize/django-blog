from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Post


class HomePageView(ListView):
    """Show the home page of the website."""

    template_name = "blog/index.html"
    context_object_name = "posts"

    def get_queryset(self):
        return Post.objects.filter(status=1)


class PostDetailView(DetailView):
    """Show the detail of a single post."""

    model = Post
    context_object_name = "post"
    template_name = "blog/post_detail.html"


class PostCreateView(LoginRequiredMixin, CreateView):
    """Display post creation form and handle the process."""

    model = Post
    fields = ["category", "title", "content", "status"]
    template_name = "blog/post_create.html"

    def form_valid(self, form):
        # assign the current logged in user as author of the post
        form.instance.author = self.request.user
        if form.instance.status == 0:
            msg = "Your post has been saved to draft."
        elif form.instance.status == 1:
            msg = "Your post has been published."
        messages.success(self.request, msg)
        return super().form_valid(form)


class PostUpdateView(UpdateView):
    pass


class PostDeleteView(DeleteView):
    pass


class CategoryView(ListView):
    pass
