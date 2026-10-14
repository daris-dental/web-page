from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import PacienteForm
from .models import Paciente


@login_required
def paciente_form(request):
    paciente, created = Paciente.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('patients:perfil')
    else:
        form = PacienteForm(instance=paciente)

    return render(request, 'patients/paciente_form.html', {
        'form': form,
        'paciente': paciente
    })


@login_required
def perfil(request):
    paciente = getattr(request.user, 'paciente', None)
    return render(request, 'patients/perfil.html', {
        'paciente': paciente
    })