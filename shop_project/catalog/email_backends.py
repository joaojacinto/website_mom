import base64
from email.utils import parseaddr

import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class BrevoEmailError(Exception):
    """Raised when Brevo rejects an email or cannot be reached."""


class BrevoEmailBackend(BaseEmailBackend):
    api_url = "https://api.brevo.com/v3/smtp/email"

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
            "sender": self._address_payload(
                message.from_email or settings.DEFAULT_FROM_EMAIL
            )[0],
            "to": self._address_payload(recipients),
            "subject": message.subject,
            "textContent": message.body,
        }
        for content, mimetype in getattr(message, "alternatives", []):
            if mimetype == "text/html":
                payload["htmlContent"] = content
                break

        if message.cc:
            payload["cc"] = self._address_payload(message.cc)
        if message.bcc:
            payload["bcc"] = self._address_payload(message.bcc)
        if message.reply_to:
            payload["replyTo"] = self._address_payload(message.reply_to[:1])[0]
        if message.attachments:
            payload["attachment"] = [
                self._attachment_payload(attachment)
                for attachment in message.attachments
            ]

        api_key = getattr(settings, "BREVO_API_KEY", "").strip()
        if not api_key:
            raise BrevoEmailError("BREVO_API_KEY must be configured.")

        try:
            response = requests.post(
                self.api_url,
                headers={
                    "api-key": api_key,
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=getattr(settings, "EMAIL_TIMEOUT", 15),
            )
        except requests.RequestException as exc:
            raise BrevoEmailError("Could not reach the Brevo API.") from exc

        if not 200 <= response.status_code < 300:
            raise BrevoEmailError(
                f"Brevo API returned HTTP {response.status_code}."
            )
        return True

    @staticmethod
    def _address_payload(addresses):
        payload = []
        address_list = (
            addresses if isinstance(addresses, (list, tuple)) else [addresses]
        )
        for address in address_list:
            name, email = parseaddr(address)
            entry = {"email": email or address}
            if name:
                entry["name"] = name
            payload.append(entry)
        return payload

    @staticmethod
    def _attachment_payload(attachment):
        if isinstance(attachment, tuple):
            filename, content, _mimetype = attachment
        else:
            filename = attachment.get_filename()
            content = attachment.get_payload(decode=True)
        if isinstance(content, str):
            content = content.encode()
        return {
            "name": filename,
            "content": base64.b64encode(content).decode("ascii"),
        }
