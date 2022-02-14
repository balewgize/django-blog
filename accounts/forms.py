from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import MyUser


class LoginForm(forms.ModelForm):
    """Form used to log a user in."""

    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    class Meta:
        model = MyUser
        fields = ["email", "password"]


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
