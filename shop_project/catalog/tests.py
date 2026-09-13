from django.test import TestCase

from .models import ContactRequest


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
