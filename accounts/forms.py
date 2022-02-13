from django import forms
from django.db import models
from django.contrib.auth.forms import UserCreationForm

from .models import MyUser


class SignupForm(UserCreationForm):
    """Form used to register the user."""

    class Meta:
        model = MyUser
        fields = ["first_name", "last_name", "email", "password1", "password2"]


class UserUpdateForm(forms.ModelForm):
    """A Form used to update user information."""

    class Meta:
        model = MyUser
        fields = ["first_name", "last_name"]
