from django.contrib import admin
from .forms import ConsultaAdminForm
from .models import Consulta, ImagenConsulta


class ImagenInline(admin.TabularInline):
    model = ImagenConsulta
    extra = 1


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    form = ConsultaAdminForm
    list_display = (
        'fecha', 'paciente', 'servicio', 'estado',
        'duracion_minutos', 'precio_usd',
    )
    list_filter = ('estado', 'servicio')
    search_fields = (
        'paciente__usuario__first_name',
        'paciente__usuario__last_name',
        'paciente__usuario__email',
    )
    date_hierarchy = 'fecha'
    inlines = [ImagenInline]
    readonly_fields = ('fecha_fin', 'duracion_minutos', 'precio_usd', 'creado', 'actualizado')