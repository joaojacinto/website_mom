import importlib
import os
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from shop_project.settings import _cloudinary_storage_config, _database_config

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


class EnsureAdminCommandTests(TestCase):
    def test_missing_environment_variables_make_no_changes(self):
        with patch.dict(os.environ, {}, clear=True):
            call_command("ensure_admin")

        self.assertFalse(get_user_model().objects.exists())

    def test_command_creates_superuser_without_exposing_password(self):
        with self._environment(
            DJANGO_ADMIN_USERNAME="admin",
            DJANGO_ADMIN_EMAIL="admin@example.com",
            DJANGO_ADMIN_PASSWORD="temporary-secret",
        ):
            output = StringIO()
            call_command("ensure_admin", stdout=output)

        user = get_user_model().objects.get(username="admin")
        self.assertEqual(user.email, "admin@example.com")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("temporary-secret"))
        self.assertNotIn("temporary-secret", output.getvalue())

    def test_command_updates_existing_user_idempotently(self):
        user = get_user_model().objects.create_user(
            username="admin",
            email="old@example.com",
            password="old-secret",
        )

        with self._environment(
            DJANGO_ADMIN_USERNAME="admin",
            DJANGO_ADMIN_EMAIL="new@example.com",
            DJANGO_ADMIN_PASSWORD="new-secret",
        ):
            call_command("ensure_admin")

        user.refresh_from_db()
        self.assertEqual(get_user_model().objects.filter(username="admin").count(), 1)
        self.assertEqual(user.email, "new@example.com")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("new-secret"))

    def test_empty_password_fails_without_creating_user(self):
        with self._environment(
            DJANGO_ADMIN_USERNAME="admin",
            DJANGO_ADMIN_EMAIL="admin@example.com",
            DJANGO_ADMIN_PASSWORD="   ",
        ):
            with self.assertRaises(CommandError):
                call_command("ensure_admin")

        self.assertFalse(get_user_model().objects.exists())

    @staticmethod
    def _environment(**values):
        return patch.dict(os.environ, values, clear=True)


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
