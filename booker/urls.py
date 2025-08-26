from django.urls import path

from booker.views import (
    IndexListView, EventListView, EventDetailView,
    TourDetailView, TourListView, activate,
    register_view, logout_view, to_profile, TicketListView, UserUpdateView, CustomPasswordChangeView, BandListView,
    BookTicketView, buy_ticket, delete_ticket, create_ticket
)

app_name = "booker"

urlpatterns = [
    path("", IndexListView.as_view(), name="index"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("activate/<str:uid>/<str:token>/", activate, name="activate"),
    path("profile/", to_profile, name="profile"),
    path("profile/tickets/", TicketListView.as_view(), name="profile-tickets"),
    path("profile/update/", UserUpdateView.as_view(), name="profile-user-update"),
    path("profile/password/update/", CustomPasswordChangeView.as_view(), name="profile-password-update"),
    path("tickets/<int:pk>/", BookTicketView.as_view(), name="book-ticket"),
    path("tickets/<int:event_id>/buy/", buy_ticket, name="buy-ticket"),
    path("tickets/<int:event_id>/create/<int:zone_id>/", create_ticket, name="create-ticket"),
    path("tickets/<int:ticket_id>/delete/", delete_ticket, name="delete-ticket"),
    path("events/", EventListView.as_view(), name="event-list"),
    path("events/<int:pk>/", EventDetailView.as_view(), name="event-detail"),
    path("tours/", TourListView.as_view(), name="tour-list"),
    path("tours/<int:pk>/", TourDetailView.as_view(), name="tour-detail"),
    path("bands/", BandListView.as_view(), name="band-list"),
]