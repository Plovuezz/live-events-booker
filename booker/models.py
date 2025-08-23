from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import CASCADE, SET_NULL, Q


class Band(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(null=True, blank=True)
    genre = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.ImageField(upload_to="bands/", null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.genre}"


class BandInfo(models.Model):
    web_page = models.URLField(null=True, blank=True)
    band = models.OneToOneField(
        Band, on_delete=CASCADE, related_name="info"
    )

    def __str__(self):
        return f"{self.band.name} info"


class Location(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    photo = models.ImageField(upload_to="locations/", null=True, blank=True)

    def __str__(self):
        return f"{self.name}, {self.city}"


class Event(models.Model):
    band = models.ForeignKey(Band, on_delete=CASCADE, related_name="events")
    location = models.ForeignKey(
        Location, on_delete=CASCADE, related_name="events"
    )
    photo = models.ImageField(upload_to="events/", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.band.name}, {self.location}, {self.date.strftime('%A %-d, %Y')}"


class Zone(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(decimal_places=2, max_digits=9)
    capacity = models.PositiveIntegerField()
    location = models.ForeignKey(
        Location, on_delete=CASCADE, related_name="zones"
    )
    has_seats = models.BooleanField(default=False)
    rows = models.PositiveIntegerField(null=True, default=None)
    seats = models.PositiveIntegerField(null=True, default=None)

    def __str__(self):
        return f"{self.location.name}`s {self.name}"


class Tour(models.Model):
    events = models.ManyToManyField(Event, related_name="tours")
    description = models.TextField(null=True, blank=True)
    avatar = models.ImageField(upload_to="tours/", null=True, blank=True)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class User(AbstractUser):
    band = models.ForeignKey(
        Band, null=True, blank=True, on_delete=SET_NULL, related_name="members"
    )

    def __str__(self):
        return f"{self.username} - {self.first_name} {self.last_name}"


class Ticket(models.Model):
    class Status(models.TextChoices):
        RESERVED = "reserved", "Reserved"
        EXPIRED = "expired", "Expired"
        PURCHASED = "purchased", "Purchased"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        User, on_delete=CASCADE, related_name="tickets"
    )
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="tickets"
    )
    zone = models.ForeignKey(
        Zone, related_name="tickets", on_delete=CASCADE
    )
    added_at = models.DateTimeField(auto_now_add=True)
    row = models.PositiveIntegerField(null=True, default=None)
    seat = models.PositiveIntegerField(null=True, default=None)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RESERVED,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields= ["event", "zone", "row", "seat"],
                name="unique_ticket_per_event",
                condition=Q(row__isnull=False, seat__isnull=False)
            )
        ]

    def __str__(self):
        return f"Ticket for {self.event} in {self.zone} {self.added_at.strftime('%A %-d, %Y (%H:%M)')} ({self.status})"