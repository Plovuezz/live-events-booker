from django.shortcuts import render
from django.views import generic

from booker.models import Event


class IndexListView(generic.ListView):
    model = Event
    template_name = "booker/index.html"
