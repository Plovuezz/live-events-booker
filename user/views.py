from base64 import urlsafe_b64encode

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import generic, View

from booker.models import Ticket, Band, Tour, Event
from booker.services.token_service import account_activation_token
from user.forms import UserRegistrationForm, UserUpdateForm, UserBandAddForm


User = get_user_model()


def activate_email(request, user, to_email):

    mail_subject = "Activate your user account."

    scheme = request.scheme
    domain = get_current_site(request).domain
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)

    url = f"{scheme}://{domain}/users/activate/{uid}/{token}/"

    html_content = render_to_string(
        "registration/activate_account.html",
        {"url": url, "user": user},
    )

    email = EmailMessage(mail_subject, body=html_content, to=[to_email])
    email.content_subtype = "html"

    if email.send():
        messages.success(request, f"Activation link was sent to your email")
    else:
        messages.error(
            request,
            f"Problem sending confirmation email to {to_email}, check if you typed it correctly.",
        )


class RegisterView(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, "registration/register.html", {"form": form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activate_email(request, user, form.cleaned_data.get("email"))
            return redirect("login")
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
        return render(request, "registration/register.html", {"form": form})


class ActivateAccountView(View):
    def get(self, request, uid: str, token: str):
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None:
            if user.is_active:
                messages.info(request, "Your account is already activated.")

                return redirect("login")

            if account_activation_token.check_token(user, token):
                user.is_active = True
                user.save()

                messages.success(
                    request,
                    "Thank you for confirming your email. You can now login to your account.",
                )
                return redirect("login")

        messages.success(
            request,
            "Something went wrong, or token expired.",
        )
        return redirect("login")


class ProfileView(LoginRequiredMixin, generic.TemplateView):
    template_name = "user/user_profile.html"


class UserUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "user/user_profile_update.html"
    success_url = reverse_lazy("booker:profile")

    def get_object(self, queryset=None):
        return self.request.user


class UserAddBandView(LoginRequiredMixin, generic.UpdateView):
    model = User
    form_class = UserBandAddForm
    template_name = "user/user_profile_update.html"
    success_url = reverse_lazy("user:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        self.object.band = form.cleaned_data["invite_code"]
        return super().form_valid(form)


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = "user/user_profile_update.html"
    success_url = reverse_lazy("user:profile")


class TicketListView(LoginRequiredMixin, generic.ListView):
    model = Ticket
    template_name = "user/user_profile_tickets.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return (
            qs.filter(
                user=self.request.user,
                status__in=[Ticket.Status.PURCHASED, Ticket.Status.CANCELLED],
            )
            .select_related("zone", "event", "zone__location", "event__band")
            .order_by("-added_at")
        )


class UserBandDetail(LoginRequiredMixin, generic.DetailView):
    model = Band
    template_name = "user/user_profile_band.html"

    def get_object(self, queryset=None):
        return self.request.user.band

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event_list"] = self.object.events.select_related(
            "location", "tour"
        ).order_by("-date")
        context["tour_list"] = self.object.tours.select_related("initiator").order_by(
            "-start_time"
        )
        return context


class BandUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Band
    fields = [
        "name",
        "bio",
        "genres",
        "avatar",
    ]
    template_name = "user/band_form_update.html"
    success_url = reverse_lazy("user:profile-band")

    def get_queryset(self):
        return Band.objects.filter(members=self.request.user)


class TourUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Tour
    fields = ["description", "avatar", "title", "start_time", "is_active"]
    template_name = "user/band_form_update.html"
    success_url = reverse_lazy("user:profile-band")

    def get_queryset(self):
        return Tour.objects.filter(initiator__members=self.request.user)


class TourDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Tour
    success_url = reverse_lazy("user:profile-band")

    def get_queryset(self):
        return Tour.objects.filter(initiator__members=self.request.user)


class EventUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Event
    fields = [
        "name",
        "tour",
        "location",
        "zones",
        "photo",
        "description",
        "is_active",
        "date",
    ]
    template_name = "user/band_form_update.html"
    success_url = reverse_lazy("user:profile-band")

    def get_queryset(self):
        return Event.objects.filter(band__members=self.request.user)


class EventDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Event
    success_url = reverse_lazy("user:profile-band")

    def get_queryset(self):
        return Event.objects.filter(band__members=self.request.user)
