from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone

import settings

from .forms import ConsultaAdminForm, ImagenConsultaForm
from .models import Consulta, FechaBloqueada, ImagenConsulta
from .rules import puede_marcar_realizada, turno_disponible, turno_disponible, validar_agendamiento


@staff_member_required
def lista(request):
    hoy = timezone.localdate()
    estado = request.GET.get('estado', '')
    desde = request.GET.get('desde', '')
    hasta = request.GET.get('hasta', '')

    # Si el usuario no pasó ningún filtro, mostrar por defecto las del día
    sin_filtros = not (estado or desde or hasta)
    if sin_filtros:
        desde = hoy.isoformat()
        hasta = hoy.isoformat()

    qs = (
        Consulta.objects
        .select_related('paciente__usuario', 'servicio')
        .order_by('fecha')  # orden cronológico para el día actual
    )

    if estado:
        qs = qs.filter(estado=estado)

    if desde:
        try:
            d = datetime.strptime(desde, '%Y-%m-%d').date()
            qs = qs.filter(fecha__date__gte=d)
        except ValueError:
            pass

    if hasta:
        try:
            h = datetime.strptime(hasta, '%Y-%m-%d').date()
            qs = qs.filter(fecha__date__lte=h)
        except ValueError:
            pass

    return render(request, 'panel/consultas_lista.html', {
        'consultas': qs,
        'estado': estado,
        'desde': desde,
        'hasta': hasta,
        'estados': Consulta.ESTADOS,
        'hoy': hoy,
        'sin_filtros': sin_filtros,
    })

@staff_member_required
def detalle(request, pk, ck):
    consulta = get_object_or_404(
        Consulta, pk=pk, paciente=ck 
    )

    user = consulta.paciente.usuario
    wa_text = (
        f"Hola, soy {user.get_full_name() or user.username} "
        f"(usuario: {user.username}). "
        f"Quiero consultar sobre mi cita de «{consulta.servicio.nombre}» "
        f"del {consulta.fecha:%d/%m/%Y a las %H:%M}."
    )

    nombre = user.get_full_name() or user.username

    return render(request, 'panel/consulta_detalle.html', {
        'consulta': consulta,
        'whatsapp_number': getattr(settings, 'WHATSAPP_NUMBER', '5354783902'),
        'wa_text': wa_text,
        'nombre': nombre,
    })





@staff_member_required
def crear(request):
    if request.method == 'POST':
        form = ConsultaAdminForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'Revise el formulario e intente de nuevo.')
        else:
            servicio = form.cleaned_data['servicio']
            fecha_str = (request.POST.get('fecha') or '').strip()
            seccion = (request.POST.get('seccion') or '').strip()

            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                fecha = None

            if not fecha or seccion not in ('manana', 'tarde'):
                messages.error(
                    request,
                    'Seleccione un día y una sección en el calendario.'
                )
            else:
                turno = turno_disponible(fecha, servicio, seccion)
                if turno is None:
                    messages.error(
                        request,
                        'La franja seleccionada ya no está disponible.'
                    )
                else:
                    consulta = form.save(commit=False)
                    consulta.fecha = turno
                    errores = validar_agendamiento(
                        paciente=consulta.paciente,
                        servicio=servicio,
                        fecha_inicio=turno,
                        es_admin=True,
                    )
                    if errores:
                        for e in errores:
                            messages.error(request, e)
                    else:
                        consulta.save()
                        turno_local = timezone.localtime(consulta.fecha)
                        messages.success(
                            request,
                            f'Consulta creada para el '
                            f'{turno_local:%d/%m/%Y %H:%M}.'
                        )
                        return redirect('panel:consultas_lista')
    else:
        initial = {}
        paciente_id = request.GET.get('paciente')
        if paciente_id:
            initial['paciente'] = paciente_id
        form = ConsultaAdminForm(initial=initial)

    return render(request, 'panel/consultas_form.html', {
        'form': form, 'accion': 'Crear',
    })


@staff_member_required
def editar(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk)
    marcar = request.GET.get('marcar', '')

    if request.method == 'POST':
        form = ConsultaAdminForm(request.POST, instance=consulta)
        if not form.is_valid():
            messages.error(request, 'Revise el formulario e intente de nuevo.')
        else:
            servicio = form.cleaned_data['servicio']
            fecha_str = (request.POST.get('fecha') or '').strip()
            seccion = (request.POST.get('seccion') or '').strip()

            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                fecha = None

            if not fecha or seccion not in ('manana', 'tarde'):
                consulta = form.save()
                messages.success(request, 'Consulta actualizada.')
                return redirect('panel:consultas_lista')

            turno = turno_disponible(
                fecha, servicio, seccion, consulta_id=consulta.pk
            )
            if turno is None:
                messages.error(request, 'Franja no disponible.')
            else:
                consulta = form.save(commit=False)
                consulta.fecha = turno
                errores = validar_agendamiento(
                    paciente=consulta.paciente,
                    servicio=servicio,
                    fecha_inicio=turno,
                    consulta_id=consulta.pk,
                    es_admin=True,
                )
                if errores:
                    for e in errores:
                        messages.error(request, e)
                else:
                    consulta.save()
                    messages.success(request, 'Consulta actualizada.')
                    return redirect('panel:consultas_lista')
    else:
        form = ConsultaAdminForm(instance=consulta)

        # Si venimos de "Marcar realizada", premarcamos el estado
        if marcar == 'realizada' and consulta.estado != 'realizada':
            form.initial['estado'] = 'realizada'

    return render(request, 'panel/consultas_form.html', {
        'form': form,
        'accion': 'Editar',
        'consulta': consulta,
        'marcar': marcar,
    })


@staff_member_required
def eliminar(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk)
    if request.method == 'POST':
        consulta.delete()
        messages.success(request, 'Consulta eliminada.')
        return redirect('panel:consultas_lista')
    return render(request, 'panel/confirmar_eliminar.html', {
        'objeto': consulta, 'titulo': 'consulta',
        'cancelar_url': 'panel:consultas_lista',
    })

@staff_member_required
def eliminar_masivo(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids')
        if ids:
            n, _ = Consulta.objects.filter(pk__in=ids).delete()
            messages.success(request, f'{len(ids)} consulta(s) eliminada(s).')
        else:
            messages.warning(request, 'No seleccionó ninguna consulta.')
    return redirect('panel:consultas_lista')

@staff_member_required
def marcar_estado(request, pk, estado):
    consulta = get_object_or_404(Consulta, pk=pk)
    if estado in dict(Consulta.ESTADOS):
        consulta.estado = estado
        consulta.save()
        messages.success(
            request, f'Consulta marcada como {consulta.get_estado_display()}.'
        )
    return redirect('panel:consultas_lista')


@staff_member_required
def marcar_realizada(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk)

    puede, faltan = puede_marcar_realizada(consulta)
    if not puede:
        
        # Redirigir al form con ?marcar=realizada
        url = reverse('panel:consultas_editar', args=[consulta.pk])
        return redirect(f'{url}?marcar=realizada')

    consulta.estado = 'realizada'
    consulta.save(update_fields=['estado', 'actualizado'])
    messages.success(request, 'Consulta marcada como realizada.')
    return redirect('panel:consultas_lista')


@staff_member_required
def marcar_confirmada(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk)
    if consulta.estado == 'pendiente':
        consulta.estado = 'confirmada'
        consulta.save(update_fields=['estado', 'actualizado'])
        messages.success(request, 'Consulta confirmada.')
    else:
        messages.info(
            request,
            f'La consulta ya está en estado «{consulta.get_estado_display()}».'
        )
    return redirect('panel:consultas_lista')


# --- Días bloqueados ---

from datetime import datetime


@staff_member_required
def fechas_bloqueadas(request):
    if request.method == 'POST':
        fecha_str = (request.POST.get('fecha') or '').strip()
        seccion = (request.POST.get('seccion') or 'completo').strip()
        motivo = request.POST.get('motivo', '').strip()

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, 'Seleccione una fecha válida.')
            return redirect('panel:fechas_bloqueadas')

        if seccion not in dict(FechaBloqueada.SECCIONES):
            messages.error(request, 'Sección inválida.')
            return redirect('panel:fechas_bloqueadas')

        obj, created = FechaBloqueada.objects.update_or_create(
            fecha=fecha, seccion=seccion,
            defaults={'motivo': motivo},
        )
        messages.success(
            request,
            f'{fecha:%d/%m/%Y} ({obj.get_seccion_display()}) '
            f'{"bloqueada" if created else "actualizada"}.'
        )
        return redirect('panel:fechas_bloqueadas')

    fechas = FechaBloqueada.objects.all().order_by('fecha', 'seccion')
    return render(request, 'panel/fechas_bloqueadas.html', {
        'fechas': fechas,
        'secciones': FechaBloqueada.SECCIONES,
    })


@staff_member_required
def desbloquear_fecha(request, pk):
    obj = get_object_or_404(FechaBloqueada, pk=pk)
    if request.method == 'POST':
        info = f'{obj.fecha:%d/%m/%Y} ({obj.get_seccion_display()})'
        obj.delete()
        messages.success(request, f'{info} desbloqueada.')
    return redirect('panel:fechas_bloqueadas')




@staff_member_required
def desbloquear_dia(request, pk):
    obj = get_object_or_404(FechaBloqueada, pk=pk)
    if request.method == 'POST':
        nombre = obj.get_dia_semana_display()
        obj.delete()
        messages.success(request, f'{nombre} desbloqueado.')
    return redirect('panel:dias_bloqueados')

import json
from django.http import JsonResponse


@staff_member_required
def subir_imagen(request, pk):
    """Sube una imagen a la consulta indicada. Acepta AJAX y formulario clásico."""
    consulta = get_object_or_404(Consulta, pk=pk)

    if request.method == 'POST':
        form = ImagenConsultaForm(request.POST, request.FILES)
        if form.is_valid():
            imagen = form.save(commit=False)
            imagen.consulta = consulta
            imagen.save()

            # Respuesta AJAX si lo pide el cliente
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'imagen': {
                        'id': imagen.pk,
                        'url': imagen.imagen.url,
                        'descripcion': imagen.descripcion or '',
                        'subida': imagen.subida.strftime('%d/%m/%Y %H:%M'),
                    }
                })

            messages.success(request, 'Imagen añadida a la consulta.')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                }, status=400)
            messages.error(request, 'No se pudo subir la imagen.')

        return redirect('panel:consultas_editar', pk=consulta.pk)

    form = ImagenConsultaForm()
    return render(request, 'panel/consultas_subir_imagen.html', {
        'consulta': consulta,
        'form': form,
    })


@staff_member_required
def eliminar_imagen(request, pk):
    imagen = get_object_or_404(ImagenConsulta, pk=pk)
    consulta_pk = imagen.consulta.pk

    if request.method == 'POST':
        imagen.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        messages.success(request, 'Imagen eliminada.')

    return redirect('panel:consultas_editar', pk=consulta_pk)