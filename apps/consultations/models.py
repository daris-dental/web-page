from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.patients.models import Paciente
from apps.services.models import Servicio


ESTADOS_ACTIVOS = ('pendiente', 'confirmada')


class Consulta(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
    ]

    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name='consultas'
    )
    servicio = models.ForeignKey(
        Servicio, on_delete=models.PROTECT, related_name='consultas'
    )
    fecha = models.DateTimeField('inicio')
    fecha_fin = models.DateTimeField(editable=False, null=True)
    duracion_minutos = models.PositiveIntegerField(editable=False, default=0)
    precio_usd = models.DecimalField(
        'precio (USD)', max_digits=8, decimal_places=2, editable=False, default=0
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    proxima_visita = models.DateField(
    'próxima visita',
    null=True, blank=True,
    help_text='Fecha sugerida para la siguiente consulta.'
    )
    notas = models.TextField('notas', blank=True)
    tratamiento = models.TextField('tratamiento', blank=True)
    medicacion = models.TextField('medicación', blank=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Consulta'
        verbose_name_plural = 'Consultas'
        indexes = [models.Index(fields=['fecha', 'fecha_fin', 'estado'])]

    def __str__(self):
        return f'{self.servicio.nombre} · {self.paciente} · {self.fecha:%Y-%m-%d %H:%M}'

    def save(self, *args, **kwargs):
        # Snapshot del servicio en el momento de agendar
        self.duracion_minutos = self.servicio.duracion_minutos
        self.precio_usd = self.servicio.precio_usd
        self.fecha_fin = self.fecha + timedelta(minutes=self.duracion_minutos)
        super().save(*args, **kwargs)

    @property
    def es_activa(self):
        return self.estado in ESTADOS_ACTIVOS

    @property
    def duracion_display(self):
        m = int(self.duracion_minutos or 0)
        if m < 60:
            return f'{m} min'
        h, r = divmod(m, 60)
        return f'{h} h' if r == 0 else f'{h} h {r} min'


class ImagenConsulta(models.Model):
    consulta = models.ForeignKey(
        Consulta, on_delete=models.CASCADE, related_name='imagenes'
    )
    imagen = models.ImageField('imagen', upload_to='consultas/%Y/%m/')
    descripcion = models.CharField('descripción', max_length=200, blank=True)
    subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Imagen de consulta'
        verbose_name_plural = 'Imágenes de consulta'

    def __str__(self):
        return f'Imagen de {self.consulta_id} ({self.descripcion or "sin descripción"})'

class FechaBloqueada(models.Model):
    SECCIONES = [
        ('completo', 'Todo el día'),
        ('manana', 'Solo mañana (9–12)'),
        ('tarde', 'Solo tarde (13–18)'),
    ]

    fecha = models.DateField('fecha')
    seccion = models.CharField(
        'sección', max_length=10, choices=SECCIONES, default='completo'
    )
    motivo = models.CharField('motivo', max_length=200, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('fecha', 'seccion')
        ordering = ['fecha', 'seccion']
        verbose_name = 'Fecha bloqueada'
        verbose_name_plural = 'Fechas bloqueadas'

    def __str__(self):
        return f'{self.fecha:%d/%m/%Y} ({self.get_seccion_display()}) — {self.motivo or "sin motivo"}'