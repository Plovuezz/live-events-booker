from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from booker.models import Event, Band, Tour, Location, Zone, Ticket

User = get_user_model()

avatar = SimpleUploadedFile(
    name="test_avatar.jpg", content=b"fake image content", content_type="image/jpeg"
)


class IndexListViewTests(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            name="Test Hall",
            description="Test description",
            country="UA",
            city="Kyiv",
            address="Test street 1",
        )

        self.band = Band.objects.create(
            name="Test Band",
            bio="Some bio",
            avatar=avatar,
        )

        self.tour = Tour.objects.create(
            title="Test Tour",
            description="Tour description",
            start_time=timezone.now() + timezone.timedelta(days=1),
            initiator=self.band,
            is_active=True,
        )

        self.event = Event.objects.create(
            name="Future Event",
            band=self.band,
            tour=self.tour,
            location=self.location,
            is_active=True,
            date=timezone.now() + timezone.timedelta(days=2),
        )

    def test_index_view_renders_correct_template(self):
        response = self.client.get(reverse("booker:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "booker/index.html")

    def test_index_view_context_contains_events_tours_bands(self):
        response = self.client.get(reverse("booker:index"))
        self.assertIn("event_list", response.context)
        self.assertIn(self.event, response.context["object_list"])

        self.assertIn("tour_list", response.context)
        self.assertIn(self.tour, response.context["tour_list"])

        self.assertIn("band_list", response.context)
        self.assertIn(self.band, response.context["band_list"])


class BookTicketViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.band = Band.objects.create(name="Test Band")
        self.location = Location.objects.create(name="Test Hall")
        self.event = Event.objects.create(
            name="Test Event",
            band=self.band,
            location=self.location,
            date=timezone.now() + timezone.timedelta(days=1),
            is_active=True,
        )
        self.zone = Zone.objects.create(
            name="VIP", location=self.location, price=100, capacity=100
        )
        self.event.zones.add(self.zone)
        self.url = reverse("booker:book-ticket", args=[self.event.id])

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/accounts/login/?next={self.url}")

    def test_view_with_logged_user(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "booker/book_ticket.html")
        self.assertEqual(response.context["event"], self.event)
        self.assertIn((self.zone, 100), response.context["zones"])


class CreateBuyDeleteTicketTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.other_user = User.objects.create_user(
            username="other", password="password123"
        )
        self.band = Band.objects.create(name="Test Band")
        self.location = Location.objects.create(name="Test Hall")
        self.event = Event.objects.create(
            name="Test Event",
            band=self.band,
            location=self.location,
            date=timezone.now() + timezone.timedelta(days=1),
            is_active=True,
        )
        self.zone = Zone.objects.create(
            name="VIP", location=self.location, price=100, capacity=100
        )
        self.event.zones.add(self.zone)
        self.url = reverse("booker:create-ticket", args=[self.event.id, self.zone.id])

    def test_create_ticket_success(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.post(self.url, {"zone": self.zone.id})
        self.assertEqual(response.status_code, 302)
        ticket = Ticket.objects.first()
        self.assertEqual(ticket.user, self.user)
        self.assertEqual(ticket.zone, self.zone)
        self.assertEqual(ticket.event, self.event)

    def test_buy_ticket_owner(self):
        self.client.login(username="testuser", password="password123")

        create_url = reverse("booker:create-ticket", args=[self.event.id, self.zone.id])
        self.client.post(create_url)

        buy_url = reverse("booker:buy-ticket", args=[self.event.id])
        response = self.client.post(buy_url)

        self.assertTemplateUsed(response, "booker/purchase_success.html")

        ticket = Ticket.objects.first()
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, Ticket.Status.PURCHASED)

    def test_delete_ticket(self):
        self.client.login(username="testuser", password="password123")
        self.client.post(
            reverse("booker:create-ticket", args=[self.event.id, self.zone.id])
        )
        ticket = Ticket.objects.first()

        delete_url = reverse("booker:delete-ticket", args=[ticket.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Ticket.objects.filter(id=ticket.id).exists())

    def test_cannot_delete_other_users_ticket(self):
        self.client.login(username="testuser", password="password123")
        self.client.post(
            reverse("booker:create-ticket", args=[self.event.id, self.zone.id])
        )
        ticket = Ticket.objects.first()

        self.client.login(username="other", password="password123")
        delete_url = reverse("booker:delete-ticket", args=[ticket.id])
        response = self.client.post(delete_url)

        self.assertEqual(response.status_code, 404)
