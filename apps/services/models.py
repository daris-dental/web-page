from django.db import models


class Servicio(models.Model):
    nombre = models.CharField('nombre', max_length=120, unique=True)
    descripcion = models.TextField('descripción', blank=True)
    duracion_minutos = models.PositiveIntegerField('duración (min)', default=30)
    precio_usd = models.DecimalField('precio (USD)', max_digits=8, decimal_places=2)
    imagen = models.ImageField('imagen', upload_to='servicios/', blank=True, null=True,)
    activo = models.BooleanField('activo', default=True)
    ocupa_dia_completo = models.BooleanField(
    'ocupa el día completo',
    default=False,
    help_text='Ej: Diseño de sonrisa. Ocupa de 9:00 a 18:00 y solo se agenda si el día está libre.'
    )
    agendable_web = models.BooleanField(
        'agendable en web',
        default=True,
        help_text='Desmarcar para servicios que solo gestiona el administrador (ej. Ortodoncia).'
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'

    def __str__(self):
        return f'{self.nombre} ({self.duracion_minutos} min · {self.precio_usd} USD)'

    @property
    def duracion_display(self):
        """Devuelve '1 h 30 min', '1 h', '45 min', etc."""
        m = int(self.duracion_minutos or 0)
        if m < 60:
            return f'{m} min'
        h, r = divmod(m, 60)
        return f'{h} h' if r == 0 else f'{h} h {r} min'

class Articulo(models.Model):
    ESTADOS = [
        ('en_stock', 'En stock'),
        ('agotado', 'Agotado'),
    ]

    nombre = models.CharField('nombre', max_length=120, unique=True)
    descripcion = models.TextField('descripción', blank=True)
    precio_usd = models.DecimalField('precio (USD)', max_digits=8, decimal_places=2)
    unidad = models.CharField(
        'unidad', max_length=50, blank=True,
        help_text='Ej: unidad, caja, frasco, par'
    )
    imagen = models.ImageField(
        'imagen', upload_to='articulos/', blank=True, null=True,
    )
    estado = models.CharField(
        'estado', max_length=20, choices=ESTADOS, default='en_stock',
    )
    activo = models.BooleanField(
        'visible al público', default=True,
        help_text='Desmarcar para ocultarlo de la web sin eliminarlo.'
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Artículo'
        verbose_name_plural = 'Artículos'

    def __str__(self):
        return f'{self.nombre} ({self.precio_usd} USD)'

    @property
    def disponible(self):
        return self.activo and self.estado == 'en_stock'

    