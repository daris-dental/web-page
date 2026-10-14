from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.consultations.models import Consulta
from apps.patients.models import Paciente
from apps.services.models import Servicio


@staff_member_required
def home(request):
    hoy = timezone.localdate()
    inicio_mes = hoy.replace(day=1)

    contexto = {
        'total_pacientes': Paciente.objects.count(),
        'total_servicios': Servicio.objects.filter(activo=True).count(),
        'consultas_pendientes': Consulta.objects.filter(estado='pendiente').count(),
        'consultas_hoy': Consulta.objects.filter(fecha__date=hoy).count(),
        'consultas_mes': Consulta.objects.filter(fecha__date__gte=inicio_mes).count(),
        'ultimas_consultas': (
            Consulta.objects
            .select_related('paciente__usuario', 'servicio')
            .order_by('-creado')[:8]
        ),
    }
    return render(request, 'panel/home.html', contexto)

def landing(request):
    if request.user.is_authenticated:
        return redirect('patients:perfil')
    return render(request, 'landing.html')