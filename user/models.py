from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import SET_NULL

from booker.models import Band


class User(AbstractUser):
    band = models.ForeignKey(
        Band, null=True, blank=True, on_delete=SET_NULL, related_name="members"
    )

    def __str__(self):
        return f"{self.username} - {self.first_name} {self.last_name}"
