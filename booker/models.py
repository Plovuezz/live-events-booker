import random

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import CASCADE
from django.utils import timezone


class Genre(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Band(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(null=True, blank=True)
    genres = models.ManyToManyField(Genre, related_name="bands")
    avatar = models.ImageField(upload_to="bands/")
    invite_code = models.CharField(max_length=255, unique=True, null=True, blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.invite_code:
            alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            while True:
                code = "".join(random.choice(alphabet) for _ in range(10))
                if not Band.objects.filter(invite_code=code).exists():
                    self.invite_code = code
                    break

        super().save(**kwargs)


class BandInfo(models.Model):
    web_page = models.URLField(null=True, blank=True)
    band = models.OneToOneField(Band, on_delete=CASCADE, related_name="info")

    class Meta:
        ordering = ("band",)

    def __str__(self):
        return f"{self.band.name} info"


class Location(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    photo = models.ImageField(upload_to="locations/", null=True, blank=True)

    class Meta:
        ordering = ("name", "city")

    def __str__(self):
        return f"{self.name}, {self.city}"


class Tour(models.Model):
    description = models.TextField(null=True, blank=True)
    avatar = models.ImageField(upload_to="tours/", null=True, blank=True)
    title = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    initiator = models.ForeignKey(Band, related_name="tours", on_delete=CASCADE)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ("title", "initiator")

    def __str__(self):
        return self.title


class Zone(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(decimal_places=2, max_digits=9)
    capacity = models.PositiveIntegerField()
    location = models.ForeignKey(Location, on_delete=CASCADE, related_name="zones")

    class Meta:
        ordering = ("location", "name")

    def __str__(self):
        return f"{self.location.name}'s {self.name}"


class Event(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    band = models.ForeignKey(Band, on_delete=CASCADE, related_name="events")
    tour = models.ForeignKey(
        Tour, on_delete=CASCADE, related_name="events", null=True, blank=True
    )
    location = models.ForeignKey(Location, on_delete=CASCADE, related_name="events")
    zones = models.ManyToManyField(Zone, related_name="events")
    photo = models.ImageField(upload_to="events/", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    date = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["location", "date"], name="unique_date_and_location"
            )
        ]
        ordering = ["date"]

    def clean(self):
        super().clean()
        if self.date < timezone.now():
            raise ValidationError({"date": "Date cant be in the past!"})

    def __str__(self):
        return (
            f"{self.band.name}, {self.location}, {self.date.strftime('%Y-%m-%d %H:%M')}"
        )


class Ticket(models.Model):
    class Status(models.TextChoices):
        RESERVED = "reserved", "Reserved"
        PURCHASED = "purchased", "Purchased"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name="tickets"
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tickets")
    zone = models.ForeignKey(Zone, related_name="tickets", on_delete=CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RESERVED,
    )

    class Meta:
        ordering = ("-added_at",)

    def __str__(self):
        return f"{self.zone} on {self.event} {self.added_at.strftime('%A %d, %Y (%H:%M)')} ({self.status})"
