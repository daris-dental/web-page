# apps/common/emailjs_backend.py
import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

class EmailJSEmailBackend(BaseEmailBackend):
    """
    Backend de correo que envía emails a través de la API REST de EmailJS.
    Usa el puerto 443 (HTTPS), permitido en Render.
    No requiere verificación de dominio.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.public_key = settings.EMAILJS_PUBLIC_KEY
        self.private_key = settings.EMAILJS_PRIVATE_KEY
        self.service_id = settings.EMAILJS_SERVICE_ID
        self.template_id = settings.EMAILJS_TEMPLATE_ID
        self.api_url = "https://api.emailjs.com/api/v1.0/email/send"

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        sent_count = 0
        for message in email_messages:
            try:
                # EmailJS espera un solo destinatario por petición en este formato
                for recipient in message.to:
                    payload = {
                        "user_id": self.public_key,
                        "accessToken": self.private_key,
                        "service_id": self.service_id,
                        "template_id": self.template_id,
                        "template_params": {
                            "to_email": recipient,
                            "from_name": message.from_email,
                            "subject": message.subject,
                            "message": message.body,
                        }
                    }

                    headers = {
                        "Content-Type": "application/json",
                    }

                    response = requests.post(
                        self.api_url,
                        json=payload,
                        headers=headers,
                        timeout=10,
                    )
                    response.raise_for_status()
                    sent_count += 1

            except requests.RequestException as e:
                if not self.fail_silently:
                    error_detail = getattr(e.response, 'text', str(e))
                    raise Exception(
                        f"Error enviando correo con EmailJS: {error_detail}"
                    )
        return sent_count