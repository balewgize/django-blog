"""Helper functions used across all apps."""

from django.utils.text import slugify
from django.utils.crypto import get_random_string


def generate_slug(Klass, base_word):
    """
    Return unique slug generated from the given base_word that is
    unique in the Klass.
    """
    unique_slug = slugify(base_word)
    is_taken = Klass.objects.filter(slug=unique_slug).exists()

    while is_taken:
        random_string = get_random_string(length=6)
        unique_slug = slugify(f"{base_word} {random_string}")
        is_taken = Klass.objects.filter(slug=unique_slug).exists()
    else:
        return unique_slug


def generate_uid(Klass):
    """Generate 12 character random string that is unique in the Klass."""
    uid = get_random_string(length=12)
    is_taken = Klass.objects.filter(uid=uid).exists()

    while is_taken:
        uid = get_random_string(length=12)
        is_taken = Klass.objects.filter(uid=uid).exists()
    else:
        return uid
