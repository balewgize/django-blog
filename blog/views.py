from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from .models import Post, Comment
from .forms import CommentForm


class HomePageView(View):
    """Show landing page of the website."""

    def get(self, request):
        # Show popular posts on the home page
        featured_posts = (
            Post.objects.select_related("category").select_related("author").all()[:10]
        )
        return render(
            request,
            "blog/landing_page.html",
            context={"featured_posts": featured_posts},
        )


class PostListView(ListView):
    """Show the list of posts."""

    template_name = "blog/index.html"
    context_object_name = "posts"
    paginate_by = 5

    def get_queryset(self):
        return (
            Post.objects.select_related("category")
            .select_related("author")
            .filter(status=1)
        )


class PostDetailView(DetailView):
    """Show the detail of a single post."""

    model = Post
    context_object_name = "post"
    template_name = "blog/post_detail.html"

    def get_queryset(self):
        return (
            Post.objects.select_related("category")
            .select_related("author")
            .filter(slug=self.kwargs["slug"])
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    """Display post creation form and handle the process."""

    model = Post
    fields = ["category", "title", "content", "status"]
    template_name = "blog/post_create.html"

    def form_valid(self, form):
        # assign the current logged in user as author of the post
        form.instance.author = self.request.user
        if form.instance.status == 0:
            msg = "Your post has been saved as draft."
        elif form.instance.status == 1:
            msg = "Your post has been published."
        messages.success(self.request, msg)
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Display post update form and handle the process."""

    model = Post
    fields = ["category", "title", "content", "status"]
    template_name = "blog/post_update.html"

    def form_valid(self, form):
        # After updating the user will be redirected to the post detail
        # page since we define get_absolute_url method in the Post model
        form.instance.author = self.request.user
        if form.instance.status == 0:
            msg = "Your post has been saved as draft."
        elif form.instance.status == 1:
            msg = "Your post has been updated."
        messages.success(self.request, msg)
        return super().form_valid(form)

    def test_func(self):
        # check that the person trying to update the post is the  owner
        return self.get_object().author == self.request.user


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Display post deletion form and handle the process."""

    model = Post
    template_name = "blog/post_delete.html"

    def get_success_url(self):
        # After deleting the post, redirect to user's profile page
        messages.info(self.request, "Your post has been deleted.")
        post_slug = self.kwargs["slug"]
        author = Post.objects.get(slug=post_slug).author
        return reverse_lazy("accounts:profile", args=(author.uid,))

    def test_func(self):
        # check that the person trying to delete the post is the owner
        return self.get_object().author == self.request.user


class CategoryView(ListView):
    """Show all post in a certain category."""

    model = Post
    template_name = "blog/category.html"
    context_object_name = "category_posts"

    def get_queryset(self):
        return (
            Post.objects.select_related("category")
            .select_related("author")
            .filter(category__slug=self.kwargs.get("slug"))
        )


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Display comment update form and handle the process."""

    model = Comment
    fields = ["content"]
    template_name = "blog/comment_update.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        # After updating the comment, redirect back to comments page
        messages.info(self.request, "Your comment has been updated.")
        post_slug = self.kwargs["slug"]
        return reverse_lazy("blog:comment-list", args=(post_slug,))

    def test_func(self):
        # check that the person trying to update the comment is the owner
        return self.get_object().author == self.request.user


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Display comment deletion form and handle the process."""

    model = Comment
    template_name = "blog/comment_delete.html"

    def get_success_url(self):
        # After deleting the comment, redirect back to comments page
        messages.info(self.request, "Your comment has been deleted.")
        post_slug = self.kwargs["slug"]
        return reverse_lazy("blog:comment-list", args=(post_slug,))

    def test_func(self):
        # check that the person trying to delete the comment is the owner
        return self.get_object().author == self.request.user


def comments(request, slug):
    """Enable user to add comments on posts."""
    comments = (
        Comment.objects.select_related("author")
        .select_related("post")
        .filter(post__slug=slug)
    )
    post = get_object_or_404(Post, slug=slug)
    if request.user.is_authenticated:
        # Only authenticated users are allowed to comment on posts
        if request.method == "POST":
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment_form.instance.author = request.user
                comment_form.instance.post = post
                comment_form.save()
                messages.info(request, "Your response has been saved.")
    else:
        # Inform users to authenticate in order to add comments
        messages.warning(request, "Login to your account to comment on posts.")

    comment_form = CommentForm()
    context = {
        "comment_form": comment_form,
        "comments": comments,
        "post": post,
    }
    return render(request, "blog/comment.html", context)


# def load_more_post(request):
#     """Load more posts dynamically."""
#     from django.core.serializers import serialize

#     limit = 5
#     offset = int(request.GET.get("offset", 1))
#     more_posts = list(
#         Post.objects.filter(status=1).values(
#             "pk",
#             "title",
#             "slug",
#             "last_update",
#             "author__first_name",
#             "author__last_name",
#             "author__uid",
#             "category__slug",
#             "category__name",
#             "content",
#         )[offset : offset + limit]
#     )

#     return JsonResponse(data={"data": more_posts}, status=200)
