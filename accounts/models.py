from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from common import utils
from blog.models import Post


class MyUserManager(BaseUserManager):
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


class MyUser(AbstractUser):
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

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "account"
        verbose_name_plural = "accounts"

    def __str__(self) -> str:
        return self.email

    def save(self, *args, **kwargs):
        """Assign unique slug before saving the user."""
        self.uid = utils.generate_uid(self.__class__)
        return super().save(*args, **kwargs)


class Bookmark(models.Model):
    """Saved posts by the user."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_bookmarking")
        ]
