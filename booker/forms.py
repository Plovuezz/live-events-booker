from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    BaseUserCreationForm,
    PasswordChangeForm,
)
from django.core.exceptions import ValidationError

from booker.models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email address")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email", "first_name", "last_name")


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name",]

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Username already exists!")
        return username
