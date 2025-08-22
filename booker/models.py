from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import CASCADE, SET_NULL


class Band(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(null=True, blank=True)
    genre = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.ImageField(upload_to="bands/", null=True, blank=True)


class BandInfo(models.Model):
    web_page = models.URLField(null=True, blank=True)
    band = models.OneToOneField(Band, on_delete=CASCADE, related_name="info")


class Location(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    photo = models.ImageField(upload_to="locations/", null=True, blank=True)


class Event(models.Model):
    band = models.ForeignKey(Band, on_delete=CASCADE, related_name="events")
    location = models.ForeignKey(Location, on_delete=CASCADE, related_name="events")
    photo = models.ImageField(upload_to="events/", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    date = models.DateTimeField()


class Zone(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(decimal_places=2, max_digits=9)
    capacity = models.PositiveIntegerField()
    location = models.ForeignKey(Location, on_delete=CASCADE, related_name="zones")
    has_seats = models.BooleanField(default=False)
    rows = models.PositiveIntegerField(null=True, default=None)
    seats = models.PositiveIntegerField(null=True, default=None)


class SittingSeat(models.Model):
    zone = models.ForeignKey(Zone, on_delete=CASCADE, related_name="sitting_seats")
    event = models.ForeignKey(Event, on_delete=CASCADE, related_name="sitting_seats")
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    is_taken = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["zone", "event", "row", "seat"], name="unique_seat"
            ),
        ]


class Tour(models.Model):
    events = models.ManyToManyField(Event, related_name="tours")
    description = models.TextField(null=True, blank=True)
    avatar = models.ImageField(upload_to="tours/", null=True, blank=True)


class User(AbstractUser):
    band = models.ForeignKey(Band, null=True, blank=True, on_delete=SET_NULL, related_name="members")


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="orders")


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=CASCADE, related_name="items")

    added_at = models.DateTimeField(auto_now_add=True)

