from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid


class Usuario(AbstractUser):
    email_verificado = models.BooleanField(default=False)
    token_verificacion = models.UUIDField(default=uuid.uuid4, editable=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    email = models.EmailField('correo electrónico', unique=True)
    prefijo_telefono = models.CharField('prefijo', max_length=6, blank=True, default='+53')
    telefono = models.CharField('teléfono', max_length=20, blank=True)
    fecha_nacimiento = models.DateField('fecha de nacimiento', null=True, blank=True)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    @property
    def telefono_completo(self):
        return f'{self.prefijo_telefono} {self.telefono}'.strip()

    @property
    def edad(self):
        if not self.fecha_nacimiento:
            return None
        hoy = timezone.localdate()
        return (
            hoy.year - self.fecha_nacimiento.year
            - ((hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        )

    def __str__(self):
        return f'{self.get_full_name()} ({self.username})'