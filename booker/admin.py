from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models.aggregates import Sum

from booker.models import (
    Band,
    Genre,
    BandInfo,
    Location,
    Tour,
    Event,
    Zone,
    Ticket,
)


class BandInfoInline(admin.StackedInline):
    model = BandInfo
    can_delete = False


@admin.register(Band)
class AdminBand(admin.ModelAdmin):
    inlines = [
        BandInfoInline,
    ]
    search_fields = ["name"]
    ordering = ["name"]
    list_filter = ("genres",)
    list_display = ("name", "display_genres")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("genres")

    def display_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genres.all()])

    display_genres.short_description = "Genres"


@admin.register(Genre)
class AdminGenre(admin.ModelAdmin):
    search_fields = ["name"]
    ordering = ["name"]


@admin.register(Location)
class AdminLocation(admin.ModelAdmin):
    search_fields = ["name"]
    ordering = ["name"]
    list_filter = (
        "city",
        "country",
    )
    list_display = ("name", "city", "country", "total_capacity")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(total_capacity=Sum("zones__capacity"))

    def total_capacity(self, obj):
        return obj.total_capacity

    total_capacity.admin_order_field = "total_capacity"


@admin.register(Event)
class AdminEvent(admin.ModelAdmin):
    list_display = ("name", "band", "location", "is_active", "date")
    list_filter = (
        "band__name",
        "location__name",
    )
    ordering = ["-date"]
    search_fields = ["name", "band__name", "location__name"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("band", "location")

    # I think this will be in case, but I am not sure how I am gonna use it/

    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     if db_field.name == "zones":
    #         obj_id = request.resolver_match.kwargs.get("object_id")
    #         if obj_id:
    #             event = Event.objects.get(pk=obj_id)
    #             kwargs["queryset"] = Zone.objects.filter(location=event.location)
    #         else:
    #             kwargs["queryset"] = Zone.objects.all()
    #     return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(Tour)
class AdminTour(admin.ModelAdmin):
    ordering = ["title"]
    search_fields = ["title"]


@admin.register(Zone)
class AdminZone(admin.ModelAdmin):
    list_display = ("name", "location", "capacity")
    search_fields = ["location__name"]
    ordering = ["-capacity"]


@admin.register(Ticket)
class AdminTicket(admin.ModelAdmin):
    list_display = ("user", "event", "zone", "added_at")
    search_fields = ["user__username", "event__name"]
    list_filter = ("user__username", "event__name", "status")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user", "event", "zone")
