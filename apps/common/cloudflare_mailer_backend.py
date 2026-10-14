import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings


class CloudflareMailerBackend(BaseEmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker_url = settings.CLOUDFLARE_WORKER_URL
        self.secret = settings.CLOUDFLARE_WORKER_SECRET

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        sent = 0
        for msg in email_messages:
            body_html = None
            for alt in msg.alternatives:
                if alt[1] == 'text/html':
                    body_html = alt[0]
                    break
            try:
                r = requests.post(
                    self.worker_url,
                    json={
                        'to': list(msg.to),
                        'subject': msg.subject,
                        'text': msg.body,
                        'html': body_html,
                    },
                    headers={'X-Auth': self.secret},
                    timeout=15,
                )
                r.raise_for_status()
                sent += 1
            except requests.RequestException as e:
                if not self.fail_silently:
                    raise Exception(f'Error vía Worker: {e}')
        return sent