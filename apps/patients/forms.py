from django import forms
from apps.common.mixins import BootstrapFormMixin
from .models import Paciente


class PacienteForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ('alergias', 'medicacion', 'pais')
        widgets = {
            'alergias': forms.Textarea(attrs={'rows': 3}),
            'medicacion': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'alergias': 'Alergias conocidas',
            'medicacion': 'Medicación habitual',
            'pais': 'País',
        }