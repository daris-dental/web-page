from django import forms

from apps.common.mixins import BootstrapFormMixin
from .models import Consulta, ImagenConsulta, Paciente, Servicio
from .rules import validar_agendamiento
#from sticky_uploads.widgets import StickyUploadWidget


class ConsultaForm(BootstrapFormMixin, forms.ModelForm):
    """
    Solo servicio + notas. La fecha y la sección las envía el calendario
    por POST directo (no son campos del form).
    """

    class Meta:
        model = Consulta
        fields = ('servicio', 'notas')
        widgets = {'notas': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['servicio'].queryset = (
            self.fields['servicio'].queryset
            .filter(activo=True, agendable_web=True)
            .order_by('nombre')
        )
        self.fields['servicio'].empty_label = '— Seleccione un servicio —'


class ConsultaAdminForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Consulta
        fields = (
            'paciente', 'servicio', 'estado',
            'notas', 'tratamiento', 'medicacion',
            'proxima_visita',
        )
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 3}),
            'tratamiento': forms.Textarea(attrs={'rows': 3}),
            'medicacion': forms.Textarea(attrs={'rows': 3}),
            'proxima_visita': forms.DateInput(attrs={'type': 'date', 'lang': 'es-CU'}),
        }

    def __init__(self, *args, **kwargs):
        paciente_id = kwargs.pop('paciente_id', None)
        super().__init__(*args, **kwargs)

        from apps.patients.models import Paciente
        self.fields['paciente'].queryset = (
            Paciente.objects.select_related('usuario')
            .order_by('usuario__first_name', 'usuario__last_name')
        )

        # Si estamos EDITANDO una consulta existente, bloquear paciente
        if self.instance and self.instance.pk:
            self.fields['paciente'].disabled = True
            self.fields['paciente'].help_text = (
                'No se puede modificar el paciente de una consulta existente. '
                'Si necesita moverla a otro paciente, elimine esta consulta y cree una nueva.'
            )
        elif paciente_id:
            try:
                self.fields['paciente'].initial = Paciente.objects.get(pk=paciente_id)
            except Paciente.DoesNotExist:
                pass

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('estado') == 'realizada':
            if not (cleaned.get('tratamiento') or '').strip():
                self.add_error('tratamiento', 'Obligatorio para marcar como realizada.')
        return cleaned



class ImagenConsultaForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ImagenConsulta
        fields = ('imagen', 'descripcion')
        widgets = {
            'descripcion': forms.TextInput(attrs={
                'placeholder': 'Ej. Radiografía panorámica, antes/después…'
            }),
        }