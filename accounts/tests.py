from datetime import datetime, timedelta
from unittest.mock import patch
from urllib.parse import urlsplit

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import override_settings
from django.urls import resolve, reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
)
class PasswordResetAPITests(APITestCase):
    """Exercise reset emails and password confirmation through the API."""

    old_password = "OriginalPassword123!"
    new_password = "ChangedPassword456!"

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            email="reset@example.com",
            password=cls.old_password,
            is_active=True,
        )
        cls.other_user = get_user_model().objects.create_user(
            email="other@example.com",
            password=cls.old_password,
            is_active=True,
        )

    def setUp(self):
        self.reset_url = reverse("reset-password")
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.confirm_url = reverse(
            "confirm-password",
            kwargs={"uidb64": self.uidb64, "token": self.token},
        )
        self.password_data = {
            "new_password": self.new_password,
            "confirm_password": self.new_password,
        }

    def assert_password_unchanged(self):
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.old_password))

    def test_reset_sends_email_with_valid_link_without_changing_password(self):
        response = self.client.post(
            self.reset_url, {"email": self.user.email}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {"detail": "An email has been sent to reset your password."},
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        link = next(
            line for line in mail.outbox[0].body.splitlines()
            if line.startswith("http")
        )
        match = resolve(urlsplit(link).path)
        self.assertEqual(match.url_name, "confirm-password")
        self.assertEqual(match.kwargs["uidb64"], self.uidb64)
        self.assertTrue(
            default_token_generator.check_token(self.user, match.kwargs["token"])
        )
        self.assert_password_unchanged()

    def test_reset_rejects_missing_empty_invalid_and_unknown_email(self):
        for data in (
            {},
            {"email": ""},
            {"email": "not-an-email"},
            {"email": "unknown@example.com"},
        ):
            with self.subTest(data=data):
                response = self.client.post(self.reset_url, data, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertTrue(response.data)
                self.assertEqual(len(mail.outbox), 0)
        self.assert_password_unchanged()

    def test_confirm_changes_and_hashes_password_and_invalidates_token(self):
        response = self.client.post(
            self.confirm_url, self.password_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {"detail": "Your Password has been successfully reset."},
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.new_password))
        self.assertFalse(self.user.check_password(self.old_password))
        self.assertNotEqual(self.user.password, self.new_password)
        self.assertFalse(default_token_generator.check_token(self.user, self.token))
        self.other_user.refresh_from_db()
        self.assertTrue(self.other_user.check_password(self.old_password))

    def test_confirm_rejects_invalid_user_ids(self):
        for uidb64 in (
            "!!!",
            urlsafe_base64_encode(force_bytes("not-a-number")),
            urlsafe_base64_encode(force_bytes(self.other_user.pk + 1000)),
        ):
            with self.subTest(uidb64=uidb64):
                url = reverse(
                    "confirm-password",
                    kwargs={"uidb64": uidb64, "token": self.token},
                )
                response = self.client.post(url, self.password_data, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assert_password_unchanged()

    def test_confirm_rejects_invalid_token_and_token_for_another_user(self):
        for token in (
            "invalid-token",
            default_token_generator.make_token(self.other_user),
        ):
            with self.subTest(token_type="invalid or other user"):
                url = reverse(
                    "confirm-password",
                    kwargs={"uidb64": self.uidb64, "token": token},
                )
                response = self.client.post(url, self.password_data, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assert_password_unchanged()

    @override_settings(PASSWORD_RESET_TIMEOUT=60)
    def test_confirm_rejects_expired_token(self):
        issued_at = datetime(2026, 1, 1, 12, 0, 0)
        with patch.object(default_token_generator, "_now", return_value=issued_at):
            token = default_token_generator.make_token(self.user)
        url = reverse(
            "confirm-password", kwargs={"uidb64": self.uidb64, "token": token}
        )

        with patch.object(
            default_token_generator, "_now",
            return_value=issued_at + timedelta(seconds=61),
        ):
            response = self.client.post(url, self.password_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assert_password_unchanged()

    def test_confirm_rejects_missing_empty_mismatched_and_short_passwords(self):
        for data in (
            {},
            {"new_password": self.new_password},
            {"confirm_password": self.new_password},
            {"new_password": "", "confirm_password": ""},
            {"new_password": self.new_password, "confirm_password": "Different123!"},
            {"new_password": "1234567", "confirm_password": "1234567"},
        ):
            with self.subTest(fields=list(data), case=data):
                response = self.client.post(self.confirm_url, data, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assert_password_unchanged()
        self.assertTrue(default_token_generator.check_token(self.user, self.token))

    def test_confirm_accepts_eight_characters(self):
        response = self.client.post(
            self.confirm_url,
            {"new_password": "Eight123", "confirm_password": "Eight123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Eight123"))

    def test_confirm_preserves_password_whitespace(self):
        password = "  ChangedPassword456!  "
        response = self.client.post(
            self.confirm_url,
            {"new_password": password, "confirm_password": password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(password))
        self.assertFalse(self.user.check_password(password.strip()))

    def test_reset_email_to_confirmation_and_login(self):
        response = self.client.post(
            self.reset_url, {"email": self.user.email}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        link = next(
            line for line in mail.outbox[0].body.splitlines()
            if line.startswith("http")
        )
        confirm_path = urlsplit(link).path
        response = self.client.post(confirm_path, self.password_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            reverse("login"),
            {"email": self.user.email, "password": self.new_password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(
            reverse("login"),
            {"email": self.user.email, "password": self.old_password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            confirm_path,
            {"new_password": "AnotherPassword789!", "confirm_password": "AnotherPassword789!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.new_password))
