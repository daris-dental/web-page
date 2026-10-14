from django.conf import settings
from django.db import models
from .countries import PAISES

class Paciente(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='paciente'
    )
    alergias = models.TextField('alergias', blank=True)
    medicacion = models.TextField('medicación', blank=True)
    pais = models.CharField(
        'país',
        max_length=2,
        choices=PAISES,
        blank=True,
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Paciente: {self.usuario.get_full_name() or self.usuario.username}'