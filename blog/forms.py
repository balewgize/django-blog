from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    """A form to accept users's comment on posts."""

    class Meta:
        model = Comment
        fields = ("content",)
