from django.urls import path
from booker.views import IndexListView

app_name = "booker"

urlpatterns = [
    path("", IndexListView.as_view(), name="index"),
]