from django.urls import path

from booker.views import (
    IndexListView,
    EventListView,
    EventDetailView,
    TourDetailView,
    TourListView,
    BandListView,
    BookTicketView,
    buy_ticket,
    delete_ticket,
    create_ticket,
)

app_name = "booker"

urlpatterns = [
    path("", IndexListView.as_view(), name="index"),

    path("tickets/<int:pk>/", BookTicketView.as_view(), name="book-ticket"),
    path("tickets/<int:event_id>/buy/", buy_ticket, name="buy-ticket"),
    path(
        "tickets/<int:event_id>/create/<int:zone_id>/",
        create_ticket,
        name="create-ticket",
    ),
    path("tickets/<int:ticket_id>/delete/", delete_ticket, name="delete-ticket"),
    path("events/", EventListView.as_view(), name="event-list"),
    path("events/<int:pk>/", EventDetailView.as_view(), name="event-detail"),
    path("tours/", TourListView.as_view(), name="tour-list"),
    path("tours/<int:pk>/", TourDetailView.as_view(), name="tour-detail"),
    path("bands/", BandListView.as_view(), name="band-list"),
]
