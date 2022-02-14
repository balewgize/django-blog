from django.db import models
from django.conf import settings
from django.urls import reverse
from ckeditor.fields import RichTextField

from common import utils


class Category(models.Model):
    """Generic category for posts."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = utils.generate_slug(self.__class__, self.name)
        super().save(*args, **kwargs)


class Post(models.Model):
    """Blog posts written by users or the admin."""

    STATUS = [(0, "Draft"), (1, "Publish")]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=206, unique=True)
    content = RichTextField()
    status = models.SmallIntegerField(choices=STATUS, default=0)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["-last_update"]

    def save(self, *args, **kwargs):
        """Assign unique slug from post title."""
        if not self.slug:
            self.slug = utils.generate_slug(self.__class__, self.title)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:post-detail", kwargs={"slug": self.slug})
