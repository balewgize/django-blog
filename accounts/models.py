from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.text import slugify
from django.utils.crypto import get_random_string


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
        error_messages={
            "unique": "An account with this email address already exists.",
        },
    )
    slug = models.SlugField(max_length=50, unique=True)
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
        self.slug = self.generate_slug()
        return super().save(*args, **kwargs)

    def generate_slug(self):
        """Return unique slug generated from full name of the User."""
        full_name = self.get_full_name()
        unique_slug = slugify(full_name)
        is_taken = MyUser.objects.filter(slug=unique_slug).exists()

        while is_taken:
            random_string = get_random_string(length=5)
            unique_slug = slugify(f"{full_name} {random_string}")
            is_taken = MyUser.objects.filter(slug=unique_slug).exists()
        else:
            return unique_slug
