from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import ListView, View

from blog.models import Post
from .forms import SignupForm, LoginForm, UserUpdateForm, ProfileUpdateForm
from .models import Account, Bookmark, Like, UserFollowing
from .tokens import email_confirmation_token


class UserProfile(ListView):
    """Show profile of the user and all posts posted by the user."""

    context_object_name = "author_posts"
    template_name = "accounts/user_profile.html"
    paginate_by = 10

    def get_queryset(self):
        # Filtering posts by the user only
        self.user = get_object_or_404(Account, uid=self.kwargs.get("uid"))
        return (
            Post.objects.filter(author=self.user)
            .select_related("category")
            .select_related("author")
            .filter(status=1)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.user
        return context


class DraftPostList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Show list of draft post that has not been published."""

    template_name = "accounts/user_draft.html"
    context_object_name = "draft_posts"

    def get_queryset(self):
        return (
            Post.objects.filter(author=self.request.user)
            .select_related("category")
            .filter(status=0)
            .order_by("-last_update")
        )

    def test_func(self):
        # check the user trying to view drafts is the owner
        self.user = get_object_or_404(Account, uid=self.kwargs.get("uid"))
        return self.request.user == self.user


class SavedPostList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Show list of bookmarked posts."""

    template_name = "accounts/user_saved.html"
    context_object_name = "bookmarks"

    def get_queryset(self):
        return (
            Bookmark.objects.select_related("post")
            .filter(user=self.request.user)
            .order_by("-saved_at")
        )

    def test_func(self):
        # check the user trying to view drafts is the owner
        self.user = get_object_or_404(Account, uid=self.kwargs.get("uid"))
        return self.request.user == self.user


class Bookmark(View):
    """Handle bookmarking post using ajax calls."""

    def post(self, request):
        user = self.request.user
        if user.is_authenticated:
            # bookmark selected post
            post_id = request.POST.get("post_id")
            selected_post = Post.objects.get(pk=post_id)
            is_bookmarked = False  # initial assumption
            bookmark = Bookmark.objects.filter(user=user, post=selected_post).first()
            if bookmark:
                # The user has already saved it, unsave now
                bookmark.delete()
            else:
                # save the bookmark now
                Bookmark.objects.create(user=user, post=selected_post)
                is_bookmarked = True
            return JsonResponse(
                {"is_bookmarked": is_bookmarked, "post_id": post_id}, status=200
            )
        else:
            # Not authenticated
            messages.warning(
                self.request,
                "Login to your account to bookmark posts.",
            )
            return JsonResponse({"is_bookmarked": False}, status=401)


class Follow(View):
    """Handle Follow and Unfollow process."""

    def post(self, request):
        current_user_id = self.request.user.pk
        if self.request.user.is_authenticated:
            # the user making the request
            current_user = Account.objects.get(pk=current_user_id)

            # ID of the user to follow or unfollow
            user_id = request.POST["user_id"]
            target_user = Account.objects.get(pk=user_id)
            is_following = False  # initial assumption

            # All users followed by current user (following wrt to the user)
            following = [f.user_following for f in current_user.following.all()]

            if not target_user in following:
                # Start following now
                print(f"I am here 2 {current_user} following {target_user} now.")
                UserFollowing.objects.create(
                    user=current_user, user_following=target_user
                )
                is_following = True
            else:
                # It was already following, Unfollow the user now
                print(f"I am here 3 {current_user} stops following {target_user} now.")
                UserFollowing.objects.filter(
                    user=current_user, user_following=target_user
                ).delete()
            return JsonResponse({"is_following": is_following}, status=200)
        else:
            messages.info(
                self.request,
                "Login to your account to follow other users.",
            )
            return JsonResponse({"not_authenticated": True}, status=401)


class Like(View):
    """Handle like and unlike posts."""

    def post(self, request):

        user = self.request.user
        if user.is_authenticated:
            # the user is authenticated, go to like activity
            user = Account.objects.get(pk=user.pk)
            post_id = request.POST.get("post_id")
            selected_post = Post.objects.get(pk=post_id)
            is_liked = False  # initial assumption
            if not selected_post in user.profile.likes:
                # Like the post now
                Like.objects.create(user=user, post=selected_post)
                is_liked = True
            else:
                # Unlike the post
                Like.objects.filter(user=user, post=selected_post).delete()

            data = {"is_liked": is_liked, "likes_count": selected_post.like_set.count()}
            return JsonResponse(data, status=200)
        else:
            messages.info(
                self.request,
                "Login to your account to like posts.",
            )
            return JsonResponse(data={"is_liked": False}, status=401)


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
            try:
                user = signup_form.save(commit=False)
                user.is_active = False  # until the user confirms the email
                user.save()

                # send verification email
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
            except Exception as error:
                print("Error: Error occurred while registering the user. Retrying...")
                print(error.with_traceback())

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
        # Automatically log the user in up on successful confirmation
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
    # Check if the user is authorized to edit the profile.
    owner = Account.objects.get(uid=uid)
    if request.user == owner:
        # can edit its own profile
        if request.method == "POST":
            user_form = UserUpdateForm(request.POST, instance=request.user)
            profile_form = ProfileUpdateForm(
                request.POST, instance=request.user.profile
            )
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
    else:
        # Can't edit others profile
        return HttpResponseForbidden("<h1>403 Forbidden</h1>")
