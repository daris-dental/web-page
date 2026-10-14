from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime, timedelta   
from .forms import ConsultaAdminForm, ConsultaForm
from .models import Consulta

from datetime import timedelta
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET
from apps.services.models import Servicio
from .rules import (
    validar_agendamiento, turno_disponible, puede_agendar, puede_cancelar,
    paciente_tiene_datos_clinicos, fecha_bloqueada, etiqueta_dia,
    DIAS_PERMITIDOS, HORAS_MINIMAS_ANTELACION,
)



@require_GET
@login_required
def disponibilidad_servicio(request, servicio_id):
    try:
        servicio = Servicio.objects.get(pk=servicio_id, activo=True)
    except Servicio.DoesNotExist:
        return JsonResponse({'error': 'Servicio no disponible'}, status=404)

    es_admin = request.user.is_staff and request.GET.get('admin') == '1'
    ahora = timezone.now()
    limite = ahora + timedelta(hours=HORAS_MINIMAS_ANTELACION)
    hoy = timezone.localdate()

    dias = []
    for offset in range(0, 60):
        dia = hoy + timedelta(days=offset)
        if not es_admin and dia.weekday() not in DIAS_PERMITIDOS:
            continue

        # Omitir días completamente bloqueados
        if fecha_bloqueada(dia, 'completo'):
            continue

        slot_m = turno_disponible(dia, servicio, 'manana')
        slot_t = turno_disponible(dia, servicio, 'tarde')

        slot_m = timezone.localtime(slot_m) if slot_m else None
        slot_t = timezone.localtime(slot_t) if slot_t else None

        if not es_admin:
            if slot_m and slot_m < limite:
                slot_m = None
            if slot_t and slot_t < limite:
                slot_t = None

        if not slot_m and not slot_t:
            continue

        dias.append({
            'fecha': dia.isoformat(),
            'label': etiqueta_dia(dia),
            'manana': slot_m.strftime('%H:%M') if slot_m else None,
            'tarde': slot_t.strftime('%H:%M') if slot_t else None,
        })

    return JsonResponse({
        'servicio': {
            'id': servicio.pk,
            'nombre': servicio.nombre,
            'ocupa_dia_completo': servicio.ocupa_dia_completo,
        },
        'dias': dias,
    })

@login_required
def agendar(request):
    from apps.patients.models import Paciente
    paciente, _ = Paciente.objects.get_or_create(usuario=request.user)

    puede, razon = puede_agendar(paciente)
    if not puede:
        return render(request, 'consultations/no_puede_agendar.html', {'razon': razon})

    clinicos, razon_c = paciente_tiene_datos_clinicos(paciente)
    if not clinicos:
        messages.warning(request, razon_c)
        return redirect('patients:paciente_form')

    # Servicio preseleccionado por URL
    servicio_id = request.GET.get('servicio', '').strip()

    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'Revise el formulario e intente de nuevo.')
        else:
            servicio = form.cleaned_data['servicio']
            fecha_str = (request.POST.get('fecha') or '').strip()
            seccion = (request.POST.get('seccion') or '').strip()

            if not fecha_str or not seccion:
                messages.error(
                    request,
                    'Debe seleccionar un día y una sección en el calendario.'
                )
            else:
                try:
                    fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                except ValueError:
                    fecha = None

                if fecha and seccion not in ('manana', 'tarde'):
                    messages.error(request, 'Sección inválida.')

                if fecha and seccion in ('manana', 'tarde'):
                    turno = turno_disponible(fecha, servicio, seccion)
                    if turno is None:
                        messages.error(
                            request,
                            'La franja seleccionada ya no está disponible. '
                            'Elija otra.'
                        )
                    else:
                        errores = validar_agendamiento(paciente, servicio, turno)
                        if errores:
                            for e in errores:
                                messages.error(request, e)
                        else:
                            consulta = form.save(commit=False)
                            consulta.paciente = paciente
                            consulta.fecha = turno
                            consulta.estado = 'pendiente'
                            consulta.save()
                            _notificar_admin(consulta)
                            turno_local = timezone.localtime(consulta.fecha)
                            messages.success(
                                request,
                                f'Consulta agendada para el '
                                f'{turno_local:%d/%m/%Y a las %H:%M}.'
                                f'Debe traer toallita o pañuelo para la saliva. Desayune antes. Si es hipertenso, tome su medicación según la pauta habitual. La puntualidad es absoluta.'
                            )
                            return redirect('consultations:detalle', pk=consulta.pk)
    else:
        initial = {}
        if servicio_id and servicio_id.isdigit():
            initial['servicio'] = int(servicio_id)
        form = ConsultaForm(initial=initial)

    return render(request, 'consultations/agendar.html', {
        'form': form,
        'servicio_id_preseleccionado': servicio_id if servicio_id.isdigit() else '',
    })


@login_required
def mis_consultas(request):
    consultas = request.user.paciente.consultas.all()
    return render(request, 'consultations/mis_consultas.html', {'consultas': consultas})


@login_required
def detalle(request, pk):
    consulta = get_object_or_404(
        Consulta, pk=pk, paciente=request.user.paciente
    )

    user = request.user
    wa_text = (
        f"Hola, soy {user.get_full_name() or user.username} "
        f"(usuario: {user.username}). "
        f"Quiero consultar sobre mi cita de «{consulta.servicio.nombre}» "
        f"del {consulta.fecha:%d/%m/%Y a las %H:%M}."
    )

    return render(request, 'consultations/detalle.html', {
        'consulta': consulta,
        'whatsapp_number': getattr(settings, 'WHATSAPP_NUMBER', '5354783902'),
        'wa_text': wa_text,
    })


def _notificar_admin(consulta):
    asunto = f'Nueva consulta agendada: {consulta.servicio.nombre}'
    mensaje = (
        f'Paciente: {consulta.paciente.usuario.get_full_name()}\n'
        f'Servicio: {consulta.servicio.nombre}\n'
        f'Fecha: {consulta.fecha:%Y-%m-%d %H:%M}\n'
        f'Duración: {consulta.duracion_minutos} min\n'
        f'Precio: {consulta.precio_usd} USD\n'
        f'Notas: {consulta.notas or "—"}\n'
    )
    send_mail(
        asunto,
        mensaje,
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],
        fail_silently=False,   # ← en producción, mejor False para ver el error
        using='default',       # ← usa el mailer "default"
    )

@staff_member_required
def crear(request):
    if request.method == 'POST':
        form = ConsultaAdminForm(request.POST)
        if form.is_valid():
            consulta = form.save()
            messages.success(
                request,
                f'Consulta creada para el {consulta.fecha:%d/%m/%Y %H:%M}.'
            )
            return redirect('panel:consultas_lista')
    else:
        form = ConsultaAdminForm(paciente_id=request.GET.get('paciente'))
    return render(request, 'panel/consultas_form.html', {
        'form': form, 'accion': 'Crear',
    })

@login_required
def cancelar(request, pk):
    consulta = get_object_or_404(
        Consulta, pk=pk, paciente=request.user.paciente
    )

    puede, razon = puede_cancelar(consulta)
    if not puede:
        messages.error(request, razon)
        return redirect('consultations:detalle', pk=consulta.pk)

    if request.method == 'POST':
        info = f'{consulta.servicio.nombre} · {consulta.fecha:%d/%m/%Y %H:%M}'
        _notificar_admin_cancelacion(consulta)
        consulta.delete()
        messages.success(
            request,
            f'Consulta cancelada y eliminada ({info}). '
        )
        return redirect('consultations:mis_consultas')

    return render(request, 'consultations/cancelar.html', {'consulta': consulta})

def _notificar_admin_cancelacion(consulta):
    asunto = f'Consulta CANCELADA: {consulta.servicio.nombre}'
    mensaje = (
        f'Paciente: {consulta.paciente.usuario.get_full_name()}\n'
        f'Servicio: {consulta.servicio.nombre}\n'
        f'Fecha: {consulta.fecha:%Y-%m-%d %H:%M}\n'
        f'Estado anterior: confirmada/pendiente\n'
    )
    send_mail(
        asunto,
        mensaje,
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],
        fail_silently=False,   # ← en producción, mejor False para ver el error
        using='default',       # ← usa el mailer "default"
    )