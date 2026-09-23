import importlib
from unittest.mock import patch

from django.conf import settings
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

from shop_project.settings import (
    _cloudinary_storage_config,
    _database_config,
    _email_config,
)

from .email_backends import ResendEmailBackend, ResendEmailError
from .models import ContactRequest, ProductImage


class DatabaseConfigurationTests(TestCase):
    def test_missing_database_url_uses_sqlite(self):
        config = _database_config(None)

        self.assertEqual(config["ENGINE"], "django.db.backends.sqlite3")

    def test_postgresql_database_url_uses_postgresql_backend(self):
        config = _database_config("postgresql:///catalog_test")

        self.assertEqual(config["ENGINE"], "django.db.backends.postgresql")
        self.assertEqual(config["NAME"], "catalog_test")

    def test_invalid_database_url_fails_explicitly(self):
        with self.assertRaises(ImproperlyConfigured):
            _database_config("not-a-database-url")


class CloudinaryConfigurationTests(TestCase):
    def test_missing_credentials_keep_local_storage_unconfigured(self):
        self.assertIsNone(_cloudinary_storage_config({}))

    def test_complete_credentials_return_cloudinary_configuration(self):
        config = _cloudinary_storage_config(
            {
                "CLOUDINARY_CLOUD_NAME": "test-cloud",
                "CLOUDINARY_API_KEY": "test-key",
                "CLOUDINARY_API_SECRET": "test-secret",
            }
        )

        self.assertEqual(
            config,
            {
                "CLOUD_NAME": "test-cloud",
                "API_KEY": "test-key",
                "API_SECRET": "test-secret",
                "PREFIX": "",
            },
        )

    def test_partial_credentials_fail_explicitly(self):
        with self.assertRaises(ImproperlyConfigured):
            _cloudinary_storage_config({"CLOUDINARY_CLOUD_NAME": "test-cloud"})

    def test_image_field_url_does_not_prefix_complete_cloudinary_url(self):
        original_storage = settings.CLOUDINARY_STORAGE
        original_media_url = settings.MEDIA_URL
        settings.CLOUDINARY_STORAGE = {
            "CLOUD_NAME": "test-cloud",
            "API_KEY": "test-key",
            "API_SECRET": "test-secret",
            "PREFIX": "",
        }
        settings.MEDIA_URL = (
            "https://res.cloudinary.com/test-cloud/image/upload/"
        )
        try:
            storage_module = importlib.import_module("cloudinary_storage.storage")
            storage = storage_module.MediaCloudinaryStorage()
            field = ProductImage._meta.get_field("image")
            expected_url = (
                "https://res.cloudinary.com/test-cloud/image/upload/"
                "product_images/vase.jpg"
            )
            resource = type("Resource", (), {"url": expected_url})()
            with patch.object(
                storage_module.cloudinary,
                "CloudinaryResource",
                return_value=resource,
            ):
                with patch.object(field, "storage", storage):
                    image = field.attr_class(
                        None,
                        field,
                        "product_images/vase.jpg",
                    )

                    self.assertEqual(image.url, expected_url)
                    self.assertNotIn("/image/upload/https://", image.url)
        finally:
            settings.CLOUDINARY_STORAGE = original_storage
            settings.MEDIA_URL = original_media_url


class EmailConfigurationTests(TestCase):
    def test_missing_credentials_use_console_backend(self):
        config = _email_config({})

        self.assertEqual(
            config,
            {
                "EMAIL_BACKEND": "django.core.mail.backends.console.EmailBackend",
                "DEFAULT_FROM_EMAIL": "webmaster@localhost",
            },
        )

    def test_resend_api_key_enables_resend_backend(self):
        config = _email_config(
            {
                "RESEND_API_KEY": "re_test_key",
                "RESEND_FROM_EMAIL": "Website <admin@example.com>",
                "EMAIL_TIMEOUT": "15",
            }
        )

        self.assertEqual(
            config,
            {
                "EMAIL_BACKEND": "catalog.email_backends.ResendEmailBackend",
                "RESEND_API_KEY": "re_test_key",
                "DEFAULT_FROM_EMAIL": "Website <admin@example.com>",
                "EMAIL_TIMEOUT": 15,
            },
        )

    def test_resend_from_email_takes_precedence_over_default_from_email(self):
        config = _email_config(
            {
                "RESEND_API_KEY": "re_test_key",
                "RESEND_FROM_EMAIL": "resend@example.com",
                "DEFAULT_FROM_EMAIL": "default@example.com",
            }
        )

        self.assertEqual(config["DEFAULT_FROM_EMAIL"], "resend@example.com")


@override_settings(
    RESEND_API_KEY="re_test_key",
    DEFAULT_FROM_EMAIL="verified@example.com",
    EMAIL_TIMEOUT=15,
)
class ResendEmailBackendTests(TestCase):
    @patch("catalog.email_backends.requests.post")
    def test_email_message_is_sent_as_resend_payload(self, post):
        post.return_value.status_code = 200
        message = EmailMultiAlternatives(
            "Reset subject",
            "Reset body",
            "verified@example.com",
            ["admin@example.com"],
        )
        message.attach_alternative("<p>Reset body</p>", "text/html")

        sent = ResendEmailBackend().send_messages([message])

        self.assertEqual(sent, 1)
        post.assert_called_once_with(
            "https://api.resend.com/emails",
            headers={
                "Authorization": "Bearer re_test_key",
                "Content-Type": "application/json",
            },
            json={
                "from": "verified@example.com",
                "to": ["admin@example.com"],
                "subject": "Reset subject",
                "text": "Reset body",
                "html": "<p>Reset body</p>",
            },
            timeout=15,
        )

    @patch("catalog.email_backends.requests.post")
    def test_non_success_response_raises_without_exposing_api_key(self, post):
        post.return_value.status_code = 401
        message = EmailMultiAlternatives(
            "Reset subject", "Reset body", to=["admin@example.com"]
        )

        with self.assertRaisesRegex(ResendEmailError, "HTTP 401") as raised:
            ResendEmailBackend().send_messages([message])

        self.assertNotIn("re_test_key", str(raised.exception))


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordResetTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        self.user = get_user_model().objects.create_user(
            username="admin",
            email="admin@example.com",
            password="Old-password-123",
            is_staff=True,
            is_superuser=True,
        )

    def test_password_reset_pages_are_available(self):
        for path in (
            "/accounts/password_reset/",
            "/accounts/password_reset/done/",
            "/accounts/reset/invalid/invalid-token/",
            "/accounts/reset/done/",
        ):
            self.assertEqual(self.client.get(path).status_code, 200)

    def test_admin_login_links_to_password_reset(self):
        response = self.client.get("/admin/login/")

        self.assertContains(response, 'href="/accounts/password_reset/"')

    def test_admin_user_can_reset_password_without_revealing_unknown_email(self):
        response = self.client.post(
            "/accounts/password_reset/",
            {"email": self.user.email},
        )

        self.assertRedirects(response, "/accounts/password_reset/done/")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("palavra-passe", mail.outbox[0].subject.lower())
        self.assertIn("/accounts/reset/", mail.outbox[0].body)

        mail.outbox.clear()
        unknown_response = self.client.post(
            "/accounts/password_reset/",
            {"email": "nobody@example.com"},
        )

        self.assertRedirects(unknown_response, "/accounts/password_reset/done/")
        self.assertEqual(len(mail.outbox), 0)

    def test_reset_link_changes_admin_password(self):
        self.client.post("/accounts/password_reset/", {"email": self.user.email})
        reset_url = next(
            line.strip()
            for line in mail.outbox[0].body.splitlines()
            if "/accounts/reset/" in line
        )
        response = self.client.get(reset_url, follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            response.request["PATH_INFO"],
            {
                "new_password1": "New-password-456",
                "new_password2": "New-password-456",
            },
        )

        self.assertRedirects(response, "/accounts/reset/done/")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("New-password-456"))


class SubmitContactTests(TestCase):
    def test_valid_post_creates_request_and_shows_success(self):
        response = self.client.post(
            "/contact/",
            {
                "name": "Ana",
                "contact_info": "ana@example.com",
                "product": "Vase",
                "message": "Em azul",
            },
        )

        self.assertRedirects(response, "/#contact")
        self.assertEqual(ContactRequest.objects.count(), 1)
        self.assertTrue(
            any("Pedido enviado" in message.message for message in response.wsgi_request._messages)
        )

    def test_success_message_renders_as_modal_after_redirect(self):
        response = self.client.post(
            "/contact/",
            {"name": "Ana", "contact_info": "ana@example.com"},
            follow=True,
        )

        self.assertContains(response, 'id="successModal"')
        self.assertContains(response, 'role="dialog"')
        self.assertNotContains(response, "site-message-success")

    def test_missing_required_contact_details_does_not_create_request(self):
        response = self.client.post(
            "/contact/", {"name": "", "contact_info": ""}, follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactRequest.objects.count(), 0)
        self.assertContains(response, "site-message-error")
        self.assertNotContains(response, 'id="successModal"')
