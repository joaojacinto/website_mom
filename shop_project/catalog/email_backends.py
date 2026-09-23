import base64

import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class ResendEmailError(Exception):
    """Raised when Resend rejects an email or cannot be reached."""


class ResendEmailBackend(BaseEmailBackend):
    api_url = "https://api.resend.com/emails"

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        sent = 0
        for message in email_messages:
            if self._send(message):
                sent += 1
        return sent

    def _send(self, message):
        recipients = message.recipients()
        if not recipients:
            return False

        payload = {
            "from": message.from_email or settings.DEFAULT_FROM_EMAIL,
            "to": recipients,
            "subject": message.subject,
            "text": message.body,
        }
        for content, mimetype in getattr(message, "alternatives", []):
            if mimetype == "text/html":
                payload["html"] = content
                break

        if message.cc:
            payload["cc"] = message.cc
        if message.bcc:
            payload["bcc"] = message.bcc
        if message.reply_to:
            payload["reply_to"] = message.reply_to
        if message.attachments:
            payload["attachments"] = [
                self._attachment_payload(attachment)
                for attachment in message.attachments
            ]

        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=getattr(settings, "EMAIL_TIMEOUT", 15),
            )
        except requests.RequestException as exc:
            raise ResendEmailError("Could not reach the Resend API.") from exc

        if not 200 <= response.status_code < 300:
            raise ResendEmailError(
                f"Resend API returned HTTP {response.status_code}."
            )
        return True

    @staticmethod
    def _attachment_payload(attachment):
        if isinstance(attachment, tuple):
            filename, content, mimetype = attachment
        else:
            filename = attachment.get_filename()
            content = attachment.get_payload(decode=True)
            mimetype = attachment.get_content_type()
        if isinstance(content, str):
            content = content.encode()
        return {
            "filename": filename,
            "content": base64.b64encode(content).decode("ascii"),
        }
