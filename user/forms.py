from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    UserCreationForm,
    BaseUserCreationForm,
    PasswordChangeForm,
)
from django.core.exceptions import ValidationError

from booker.models import Band

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email address")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email", "first_name", "last_name")


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
        ]

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Username already exists!")
        return username


class UserBandAddForm(forms.ModelForm):
    invite_code = forms.CharField(max_length=10)

    class Meta:
        model = User
        fields = ["invite_code"]

    def clean_invite_code(self):
        code = self.cleaned_data["invite_code"]
        try:
            band = Band.objects.get(invite_code=code)
        except Band.DoesNotExist:
            raise ValidationError("No band with this code!")
        return band
