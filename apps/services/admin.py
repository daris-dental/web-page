from django.contrib import admin
from .models import Servicio, Articulo


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'duracion_minutos', 'precio_usd', 'activo', 'agendable_web')
    list_filter = ('activo', 'agendable_web')
    search_fields = ('nombre',)
    list_editable = ('activo', 'agendable_web', 'precio_usd', 'duracion_minutos')

@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_usd', 'unidad', 'estado', 'activo')
    list_filter = ('estado', 'activo')
    search_fields = ('nombre',)
    list_editable = ('precio_usd', 'estado', 'activo')