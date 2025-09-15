from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic


from booker.models import Event, Tour, Ticket, Band, Zone


class IndexListView(generic.ListView):
    model = Event
    template_name = "booker/index.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return (
            qs.select_related("band", "tour", "location")
            .filter(is_active=True, date__gt=timezone.now())
            .order_by("date")[:25]
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        tours = (
            Tour.objects.filter(is_active=True)
            .select_related("initiator")
            .order_by("start_time")[:5]
        )

        bands = Band.objects.all()[:14]
        context["tour_list"] = tours
        context["band_list"] = bands
        return context


class EventListView(generic.ListView):
    model = Event

    def get_queryset(self):
        qs = super().get_queryset()
        return (
            qs.filter(is_active=True, date__gt=timezone.now())
            .select_related("band", "tour", "location")
            .order_by("date")
        )


class EventDetailView(generic.DetailView):
    model = Event


class TourListView(generic.ListView):
    model = Tour

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_active=True).order_by("start_time")


class TourDetailView(generic.DetailView):
    model = Tour


class BandListView(generic.ListView):
    model = Band
    ordering = ["name"]


class BandDetailView(generic.DetailView):
    model = Band

    def get_queryset(self):
        return Band.objects.select_related("info")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        band = self.get_object()
        context["events"] = band.events.filter(is_active=True).select_related(
            "location"
        )
        return context


class BookTicketView(LoginRequiredMixin, generic.ListView):
    model = Ticket
    template_name = "booker/book_ticket.html"

    def get_queryset(self):
        return Ticket.objects.filter(
            user=self.request.user,
            event=self.kwargs["pk"],
            status=Ticket.Status.RESERVED,
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        event = get_object_or_404(Event, id=self.kwargs["pk"])
        context["event"] = event

        zones = event.zones.annotate(
            sold=Count(
                "tickets",
                filter=Q(
                    tickets__event=event,
                    tickets__status__in=[
                        Ticket.Status.RESERVED,
                        Ticket.Status.PURCHASED,
                    ],
                ),
            )
        )

        context["zones"] = [(zone, zone.capacity - zone.sold) for zone in zones]
        tickets = context["object_list"]
        total_amount = sum(ticket.zone.price for ticket in tickets)
        total_quantity = len(tickets)
        context["total_amount"] = total_amount
        context["total_quantity"] = total_quantity
        return context


@login_required
def create_ticket(request, zone_id, event_id):
    event = get_object_or_404(Event, id=event_id)
    zone = get_object_or_404(Zone, id=zone_id)

    if (
        zone.tickets.filter(
            status__in=[Ticket.Status.RESERVED, Ticket.Status.PURCHASED]
        ).count()
        >= zone.capacity
    ):
        messages.error(request, "No tickets left")
        return redirect("booker:book-ticket")

    Ticket.objects.create(
        user=request.user, event=event, zone=zone, status=Ticket.Status.RESERVED
    )
    return redirect("booker:book-ticket", pk=event.id)


@login_required
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    event = ticket.event
    if ticket.user == request.user:
        ticket.delete()
        return redirect("booker:book-ticket", pk=event.pk)
    raise Http404()


@login_required
@transaction.atomic
def buy_ticket(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    tickets_qr = Ticket.objects.filter(user=request.user, event=event).filter(
        status=Ticket.Status.RESERVED
    )

    if tickets_qr.exists():
        tickets_qr.update(status=Ticket.Status.PURCHASED)
        return render(request, "booker/purchase_success.html")

    messages.error(
        request, "You have no tickets in cart or tickets reservation time expired"
    )
    return redirect("booker:book-ticket", pk=event_id)
