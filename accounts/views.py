from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import ListView

from blog.models import Post
from .forms import SignupForm
from .models import MyUser, Bookmark
from .tokens import email_confirmation_token


class UserProfileView(ListView):
    """Show profile of the user and all posts posted by the user."""

    context_object_name = "author_posts"
    template_name = "accounts/user_profile.html"

    def get_queryset(self):
        # Filtering posts by the user only
        self.user = get_object_or_404(MyUser, uid=self.kwargs.get("uid"))
        return (
            Post.objects.filter(author=self.user)
            .filter(status=1)
            .order_by("-last_update")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.user
        return context


class DraftPostView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Show list of draft post that has not been published."""

    template_name = "accounts/user_draft.html"
    context_object_name = "draft_posts"

    def get_queryset(self):
        return (
            Post.objects.filter(author=self.user)
            .filter(status=0)
            .order_by("-last_update")
        )

    def test_func(self):
        # check the user trying to view drafts is the owner
        self.user = get_object_or_404(MyUser, uid=self.kwargs.get("uid"))
        return self.request.user == self.user


class SavedPostView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Show list of bookmarked posts."""

    template_name = "accounts/user_saved.html"
    context_object_name = "saved_posts"

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.user).order_by("-saved_at")

    def test_func(self):
        # check the user trying to view drafts is the owner
        self.user = get_object_or_404(MyUser, uid=self.kwargs.get("uid"))
        return self.request.user == self.user


def signup(request):
    """Display signup form and handle the signup action."""

    if request.method == "POST":
        # the user has submitted the form (POST request): get the data submitted
        signup_form = SignupForm(request.POST)
        if signup_form.is_valid():
            user = signup_form.save(commit=False)
            user.is_active = False  # until the user confirms the email
            user.save()
            current_site = get_current_site(request)
            mail_subject = "Verify your email address"
            message = render_to_string(
                "accounts/confirm_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": email_confirmation_token.make_token(user),
                },
            )
            to_email = signup_form.cleaned_data.get("email")
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            # Set user email to session variable to pass it to another view
            first_name = signup_form.cleaned_data.get("first_name")
            request.session["first_name"] = first_name
            return redirect(to=reverse("accounts:verify"))
    else:
        # it is GET request: display an empty signup form
        signup_form = SignupForm()

    context = {"signup_form": signup_form}
    return render(request, "accounts/signup.html", context)


def activate(request, uidb64, token):
    """Activate the user account after the confirms their email address."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = MyUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
        user = None

    if user is not None and email_confirmation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Your email has been verified successfully.")
        messages.success(
            request, "You can now write posts and share your idea to the world."
        )
        return redirect("blog:post-list")
    else:
        return HttpResponse("Confirmation link is invalid.")


def inform_to_verify(request):
    """Inform the user to verify their email while registering."""
    first_name = request.session.get("first_name")
    if first_name:
        context = {"first_name": first_name}
    else:
        context = {"first_name": "User"}
    return render(request, "accounts/verify.html", context=context)
