import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import os
import base64 as b64
import json

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


class GmailApiBackend(BaseEmailBackend):
    """Envía correos usando la Gmail API de Google (HTTPS, no SMTP)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service = None

    def _get_service(self):
        if self._service is not None:
            return self._service

        token_path = Path(settings.BASE_DIR) / 'token.json'
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path))
        else:
            token_b64 = os.environ.get('GMAIL_TOKEN_B64', '')
            if not token_b64:
                raise RuntimeError('Falta GMAIL_TOKEN_B64 o token.json')
            data = json.loads(b64.b64decode(token_b64).decode())
            creds = Credentials.from_authorized_user_info(data)

        self._service = build('gmail', 'v1', credentials=creds, cache_discovery=False)
        return self._service

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        service = self._get_service()
        sent = 0

        for message in email_messages:
            try:
                mime = MIMEMultipart('alternative')
                mime['To'] = ', '.join(message.to)
                mime['From'] = message.from_email
                mime['Subject'] = message.subject

                mime.attach(MIMEText(message.body, 'plain', 'utf-8'))

                for alt in message.alternatives:
                    if alt[1] == 'text/html':
                        mime.attach(MIMEText(alt[0], 'html', 'utf-8'))
                        break

                raw = base64.urlsafe_b64encode(mime.as_bytes()).decode()
                service.users().messages().send(
                    userId='me', body={'raw': raw}
                ).execute()
                sent += 1

            except Exception as e:
                if not self.fail_silently:
                    raise
        return sent