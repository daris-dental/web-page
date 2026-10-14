from django import forms

from apps.common.mixins import BootstrapFormMixin
from .models import Servicio, Articulo


class ServicioForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Servicio
        fields = (
            'nombre', 'descripcion', 'duracion_minutos',
            'precio_usd', 'imagen', 'activo', 'agendable_web',
            'ocupa_dia_completo',
        )
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

class ArticuloForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Articulo
        fields = (
            'nombre', 'descripcion', 'precio_usd',
            'unidad', 'imagen', 'estado', 'activo',
        )
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }