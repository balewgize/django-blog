from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from common import utils
from blog.models import Post


class AccountManager(BaseUserManager):
    """A User manager for a custom user model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, first_name, last_name, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address.")
        if not first_name:
            raise ValueError("Users must have first name.")
        if not last_name:
            raise ValueError("Users must have last name.")

        email = self.normalize_email(email)
        user = self.model(
            email=email, first_name=first_name, last_name=last_name, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, first_name, last_name, password=None, **extrafields):
        extrafields.setdefault("is_staff", False)
        extrafields.setdefault("is_superuser", False)
        return self._create_user(email, first_name, last_name, password, **extrafields)

    def create_superuser(
        self, email, first_name, last_name, password=None, **extrafields
    ):
        extrafields.setdefault("is_staff", True)
        extrafields.setdefault("is_superuser", True)

        if extrafields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extrafields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self._create_user(email, first_name, last_name, password, **extrafields)


class Account(AbstractUser):
    """
    A class implementing a fully featured custom User model with
    admin-compliant permissions.

    first_name, last_name, email and password are required.
    """

    username = None
    email = models.EmailField(
        "email",
        max_length=200,
        unique=True,
    )
    first_name = models.CharField("first name", max_length=150)
    last_name = models.CharField("last name", max_length=150)
    uid = models.CharField("UID", max_length=12)
    is_admin = models.BooleanField(default=False)

    objects = AccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "account"
        verbose_name_plural = "accounts"

    def __str__(self) -> str:
        return self.email

    def save(self, *args, **kwargs):
        """Assign unique slug before saving the user."""
        if not self.uid:
            self.uid = utils.generate_uid(self.__class__)
        return super().save(*args, **kwargs)


class Profile(models.Model):
    """Profile of the user besides the information provided during sign up."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=150, blank=True)
    about = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.first_name}'s profile"

    @property
    def following(self):
        """All users followed by this user (following wrt to the user)."""
        return [f.user_following for f in self.user.following.all()]

    @property
    def followers(self):
        """All users following this user (follower wrt the to user)."""
        return [f.user for f in self.user.followers.all()]


class UserFollowing(models.Model):
    """
    Follower and Following relationship between users.

    user: current user
    user_following: target user current user is following
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following"
    )
    user_following = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "user_following"], name="unique_follow"
            )
        ]


class Bookmark(models.Model):
    """Saved posts by the user."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_bookmarking")
        ]


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_save_profile(sender, instance, created, **kwargs):
    """
    Automatically create a user profile after sign up or
    update it whenever user information is updated.
    """
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
