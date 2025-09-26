from django.contrib.auth.views import LogoutView
from django.urls import path

from user.views import (
    RegisterView,
    ActivateAccountView,
    ProfileView,
    TicketListView,
    UserUpdateView,
    UserAddBandView,
    UserBandDetail,
    EventUpdateView,
    EventDeleteView,
    TourUpdateView,
    TourDeleteView,
    BandUpdateView,
    CustomPasswordChangeView,
)

app_name = "user"


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "logout/",
        LogoutView.as_view(next_page="booker:index"),
        name="logout",
    ),
    path(
        "activate/<str:uid>/<str:token>/",
        ActivateAccountView.as_view(),
        name="activate",
    ),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/tickets/", TicketListView.as_view(), name="profile-tickets"),
    path("profile/update/", UserUpdateView.as_view(), name="profile-user-update"),
    path("profile/band/add/", UserAddBandView.as_view(), name="profile-band-add"),
    path("profile/band/", UserBandDetail.as_view(), name="profile-band"),
    path(
        "profile/event/<int:pk>/update/",
        EventUpdateView.as_view(),
        name="band-event-update",
    ),
    path(
        "profile/event/<int:pk>/delete/",
        EventDeleteView.as_view(),
        name="band-event-delete",
    ),
    path(
        "profile/tour/<int:pk>/update/",
        TourUpdateView.as_view(),
        name="band-tour-update",
    ),
    path(
        "profile/tour/<int:pk>/delete/",
        TourDeleteView.as_view(),
        name="band-tour-delete",
    ),
    path(
        "profile/band/<int:pk>/update/",
        BandUpdateView.as_view(),
        name="profile-band-update",
    ),
    path(
        "profile/password/update/",
        CustomPasswordChangeView.as_view(),
        name="profile-password-update",
    ),
]
