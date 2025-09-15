from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from booker.models import Band
from booker.services.token_service import account_activation_token
from user.models import User


User = get_user_model()


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_creates_inactive_user(self):
        response = self.client.post(
            reverse("user:register"),
            {
                "username": "john2131233",
                "email": "john@test.com",
                "password1": "1234!'№;",
                "password2": "1234!'№;",
            },
        )
        print(response.status_code)
        print(User.objects.all())

        user = User.objects.get(username="john2131233")
        self.assertFalse(user.is_active)
        self.assertRedirects(response, reverse("login"))


class ActivateAccountViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="john",
            email="john@test.com",
            password="Test1234!@#",
            is_active=False,
        )

    def test_activate_user_valid_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_activation_token.make_token(self.user)
        url = reverse("user:activate", args=[uid, token])

        response = self.client.get(url)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertRedirects(response, reverse("login"))

    def test_activate_user_already_active(self):
        self.user.is_active = True
        self.user.save()
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_activation_token.make_token(self.user)
        url = reverse("user:activate", args=[uid, token])

        response = self.client.get(url)
        self.assertRedirects(response, reverse("login"))

    def test_activate_user_invalid_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        invalid_token = "invalid-token"
        url = reverse("user:activate", args=[uid, invalid_token])

        response = self.client.get(url)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertRedirects(response, reverse("login"))


class ProfileViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="john", email="john@test.com", password="Test1234!@#"
        )
        self.url = reverse("user:profile")

    def test_profile_view_authenticated(self):
        self.client.login(username="john", password="Test1234!@#")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user/user_profile.html")

    def test_profile_view_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)


class UserAddBandViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="john", email="john@test.com", password="Test1234!@#"
        )
        self.band = Band.objects.create(name="TestBand", invite_code="ABC123")
        self.url = reverse("user:profile-band-add")

    def test_get_add_band_view(self):
        self.client.login(username="john", password="Test1234!@#")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user/user_profile_update.html")

    def test_post_valid_invite_code(self):
        self.client.login(username="john", password="Test1234!@#")
        response = self.client.post(self.url, {"invite_code": "ABC123"})
        self.user.refresh_from_db()
        self.assertEqual(self.user.band, self.band)
        self.assertRedirects(response, reverse("user:profile"))

    def test_post_invalid_invite_code(self):
        self.client.login(username="john", password="Test1234!@#")
        response = self.client.post(self.url, {"invite_code": "INVALID"})
        self.user.refresh_from_db()
        self.assertIsNone(self.user.band)
        self.assertEqual(response.status_code, 200)
