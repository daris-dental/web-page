from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, AuthenticationForm, PasswordChangeForm
)
from apps.common.mixins import BootstrapFormMixin
from .models import Usuario
from .prefixes import PREFIJOS


class RegistroUsuarioForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(required=True, label='Correo electrónico')
    first_name = forms.CharField(required=True, label='Nombre')
    last_name = forms.CharField(required=True, label='Apellidos')

    prefijo_telefono = forms.ChoiceField(
        required=True, label='Prefijo', choices=PREFIJOS,
    )
    telefono = forms.CharField(required=True, label='Teléfono')
    fecha_nacimiento = forms.DateField(
        required=True,
        label='Fecha de nacimiento',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    class Meta:
        model = Usuario
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'prefijo_telefono', 'telefono', 'fecha_nacimiento',
            'password1', 'password2',
        )

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe un usuario con este correo.')
        return email


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    username = forms.CharField(
        label='Usuario o correo',
        widget=forms.TextInput(attrs={'autofocus': True}),
    )


class CambiarPasswordForm(BootstrapFormMixin, PasswordChangeForm):
    pass