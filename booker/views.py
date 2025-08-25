from base64 import urlsafe_b64encode

from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode
from django.views import generic
from stone.backends.python_rsrc.stone_validators import ValidationError

from booker.forms import UserRegistrationForm, UserUpdateForm
from booker.models import Event, Tour, Ticket, User, Band
from booker.services.token_service import account_activation_token


class IndexListView(generic.ListView):
    model = Event
    template_name = "booker/index.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related("band", "tour", "location").filter(is_active=True).order_by("date")[:25]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        tours = Tour.objects.filter(is_active=True).order_by("start_time")[:5]
        bands = Band.objects.all()[:14]
        context["tour_list"] = tours
        context["band_list"] = bands
        return context


class EventListView(generic.ListView):
    model = Event
    paginate_by = 20


class EventDetailView(generic.DetailView):
    model = Event


class TourListView(generic.ListView):
    model = Tour
    paginate_by = 20


class TourDetailView(generic.DetailView):
    model = Tour


class BandListView(generic.ListView):
    model = Band
    paginate_by = 20


def logout_view(request):
    logout(request)
    return redirect("booker:index")


def activate_email(request, user, to_email):
    mail_subject = "Activate your user account."

    scheme = request.scheme
    domain = get_current_site(request).domain
    uid = urlsafe_b64encode(force_bytes(user.pk)).decode()
    token = account_activation_token.make_token(user)

    url = f"{scheme}://{domain}/activate/{uid}/{token}/"

    html_content = render_to_string(
        "registration/activate_account.html",
        {"url": url, "user": user},
    )
    email = EmailMessage(mail_subject, body=html_content, to=[to_email])

    email.content_subtype = "html"
    if email.send():
        messages.success(request, f"Activation link was sent to your email")
    else:
        messages.error(request, f"Problem sending confirmation email to {to_email}, check if you typed it correctly.")


def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activate_email(request, user, form.cleaned_data.get('email'))
            return redirect("login")

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = UserRegistrationForm()

    return render(
        request=request,
        template_name="registration/register.html",
        context={"form": form}
        )


def activate(request, uid, token):
    User = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Now you can login your account.")
        return redirect("login")
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect("booker:index")


def to_profile(request):
    return render(request, "booker/user_profile.html")


class UserUpdateView(generic.UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "booker/user_profile_update.html"
    success_url = reverse_lazy("booker:profile")

    def get_object(self, queryset=None):
        return self.request.user


class CustomPasswordChangeView(PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = "booker/user_change_password.html"
    success_url = reverse_lazy("booker:profile")


class TicketListView(generic.ListView):
    model = Ticket
    template_name = "booker/user_profile_tickets.html"