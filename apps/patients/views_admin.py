from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Paciente
from .forms import PacienteForm
from apps.accounts.forms import RegistroUsuarioForm


@staff_member_required
def lista(request):
    q = request.GET.get('q', '').strip()
    pacientes = (
        Paciente.objects
        .select_related('usuario')
        .order_by('usuario__first_name', 'usuario__last_name')
    )
    if q:
        pacientes = pacientes.filter(
            usuario__first_name__icontains=q
        ) | pacientes.filter(
            usuario__last_name__icontains=q
        ) | pacientes.filter(
            usuario__email__icontains=q
        )
    return render(request, 'panel/pacientes_lista.html', {
        'pacientes': pacientes, 'q': q,
    })


@staff_member_required
def detalle(request, pk):
    paciente = get_object_or_404(
        Paciente.objects.select_related('usuario'), pk=pk
    )
    consultas = paciente.consultas.select_related('servicio').order_by('-fecha')
    return render(request, 'panel/pacientes_detalle.html', {
        'paciente': paciente, 'consultas': consultas,
    })


@staff_member_required
def editar(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    usuario = paciente.usuario

    if request.method == 'POST':
        form_u = _UsuarioEditForm(request.POST, instance=usuario)
        form_p = PacienteForm(request.POST, instance=paciente)
        if form_u.is_valid() and form_p.is_valid():
            form_u.save()
            form_p.save()
            messages.success(request, 'Datos del paciente actualizados.')
            return redirect('panel:pacientes_detalle', pk=paciente.pk)
    else:
        form_u = _UsuarioEditForm(instance=usuario)
        form_p = PacienteForm(instance=paciente)

    return render(request, 'panel/pacientes_form.html', {
        'form_u': form_u, 'form_p': form_p, 'paciente': paciente,
    })


# Formulario ligero para editar al usuario desde el panel
from django import forms
from apps.common.mixins import BootstrapFormMixin


class _UsuarioEditForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        from apps.accounts.models import Usuario
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'telefono', 'fecha_nacimiento')
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }