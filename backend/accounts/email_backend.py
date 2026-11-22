import os
from email.utils import parseaddr

import requests
from django.core.mail.backends.base import BaseEmailBackend


class BrevoEmailBackend(BaseEmailBackend):
    """Sends e-mail over HTTPS (port 443) via the Brevo API.

    Needed on hosts that block outbound SMTP ports (e.g. Render free tier).
    Env: BREVO_API_KEY; the From address (DEFAULT_FROM_EMAIL) must be a verified sender in Brevo.
    """

    url = 'https://api.brevo.com/v3/smtp/email'

    def send_messages(self, email_messages):
        key = os.getenv('BREVO_API_KEY')
        if not key:
            if self.fail_silently:
                return 0
            raise ValueError('BREVO_API_KEY is not set')

        sent = 0
        for m in email_messages:
            name, address = parseaddr(m.from_email)
            sender = {'email': address}
            if name:
                sender['name'] = name
            payload = {
                'sender': sender,
                'to': [{'email': r} for r in m.to],
                'subject': m.subject,
                'textContent': m.body,
            }
            try:
                r = requests.post(
                    self.url, json=payload, timeout=10,
                    headers={'api-key': key, 'accept': 'application/json'},
                )
                r.raise_for_status()
                sent += 1
            except requests.RequestException:
                if not self.fail_silently:
                    raise
        return sent
