from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
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
from .forms import SignupForm, LoginForm, UserUpdateForm, ProfileUpdateForm
from .models import Account, Bookmark
from .tokens import email_confirmation_token


class UserProfileView(ListView):
    """Show profile of the user and all posts posted by the user."""

    context_object_name = "author_posts"
    template_name = "accounts/user_profile.html"

    def get_queryset(self):
        # Filtering posts by the user only
        self.user = get_object_or_404(Account, uid=self.kwargs.get("uid"))
        return (
            Post.objects.filter(author=self.user)
            .select_related("category")
            .select_related("author")
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
            .select_related("post")
            .filter(status=0)
            .order_by("-last_update")
        )

    def test_func(self):
        # check the user trying to view drafts is the owner
        self.user = get_object_or_404(Account, uid=self.kwargs.get("uid"))
        return self.request.user == self.user


class SavedPostView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Show list of bookmarked posts."""

    template_name = "accounts/user_saved.html"
    context_object_name = "bookmarks"

    def get_queryset(self):
        return (
            Bookmark.objects.select_related("post")
            .filter(user=self.user)
            .order_by("-saved_at")
        )

    def test_func(self):
        # check the user trying to view drafts is the owner
        self.user = get_object_or_404(Account, uid=self.kwargs.get("uid"))
        return self.request.user == self.user


def signin(request):
    """Display login form and handle the login process."""
    if request.user.is_authenticated:
        return redirect("blog:post-list")

    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("blog:post-list")
        else:
            messages.error(request, "Invalid Email or Password.")
    login_form = LoginForm()
    context = {"login_form": login_form}
    return render(request, "accounts/login.html", context)


def signout(request):
    """Log the user out."""
    logout(request)
    return redirect("blog:post-list")


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
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
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


@login_required
def update_profile(request, uid):
    """Update profile for authenticated user."""
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your account has been updated successfully.")
            return redirect(to=reverse("accounts:profile", args=(uid,)))
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
    }
    return render(request, "accounts/update_profile.html", context)
