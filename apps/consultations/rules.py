from datetime import datetime, time, timedelta

from django.db.models import Q
from django.utils import timezone

from .models import Consulta, FechaBloqueada, ESTADOS_ACTIVOS


# ---------------------------------------------------------------------
# Horario
# ---------------------------------------------------------------------
DIAS_PERMITIDOS = {1, 2, 3, 4, 5}          # martes=1 ... sábado=5
HORAS_MINIMAS_ANTELACION = 12
DIAS_ENTRE_CONSULTAS = 5

HORA_APERTURA = 9           # 9:00
HORA_ALMUERZO_INICIO = 12   # 12:00 — cierra la mañana
HORA_ALMUERZO_FIN = 13      # 13:00 — abre la tarde
HORA_CIERRE = 18            # 18:00


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def _aware(dt):
    if dt is None:
        return None
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def fecha_bloqueada(dia, seccion):
    """¿Está bloqueada esa fecha para esa sección? (completo aplica a todas)"""
    return FechaBloqueada.objects.filter(
        fecha=dia,
    ).filter(
        Q(seccion='completo') | Q(seccion=seccion)
    ).exists()


def _ocupadas_del_dia(dia, consulta_id=None):
    qs = Consulta.objects.filter(
        estado__in=ESTADOS_ACTIVOS,
        fecha__date=dia,
    )
    if consulta_id:
        qs = qs.exclude(pk=consulta_id)
    return sorted(qs.values_list('fecha', 'fecha_fin'))


# ---------------------------------------------------------------------
# Turno disponible
# ---------------------------------------------------------------------
def turno_disponible(dia, servicio, seccion, consulta_id=None):
    """
    Devuelve el primer datetime (aware) disponible para el servicio en la
    sección elegida, o None si no cabe.
    """

    # 1. Bloqueada esta sección
    if fecha_bloqueada(dia, seccion):
        return None

    # 2. Servicio que ocupa todo el día
    if servicio.ocupa_dia_completo:
        ocupadas = _ocupadas_del_dia(dia, consulta_id)
        if ocupadas:
            return None
        return _aware(datetime.combine(dia, time(HORA_APERTURA, 0)))

    # 3. Servicios normales
    ocupadas = _ocupadas_del_dia(dia, consulta_id)
    duracion = timedelta(minutes=servicio.duracion_minutos)

    if seccion == 'manana':
        cursor = _aware(datetime.combine(dia, time(HORA_APERTURA, 0)))
        limite = _aware(datetime.combine(dia, time(HORA_ALMUERZO_INICIO, 0)))

        for (ini, fin) in ocupadas:
            if ini >= limite:
                break
            if fin <= cursor:
                continue
            if cursor + duracion <= ini:
                return cursor
            cursor = max(cursor, fin)

        if cursor + duracion <= limite:
            return cursor
        return None

    elif seccion == 'tarde':
        cursor = _aware(datetime.combine(dia, time(HORA_ALMUERZO_FIN, 0)))
        limite = _aware(datetime.combine(dia, time(HORA_CIERRE, 0)))

        for (ini, fin) in ocupadas:
            if ini < cursor:
                continue
            if cursor + duracion <= ini:
                return cursor
            cursor = max(cursor, fin)

        if cursor + duracion <= limite:
            return cursor
        return None

    return None


# ---------------------------------------------------------------------
# Validación
# ---------------------------------------------------------------------
def validar_agendamiento(paciente, servicio, fecha_inicio, consulta_id=None, es_admin=False):
    errores = []
    ahora = timezone.now()
    fecha_inicio = _aware(fecha_inicio)
    fecha_fin = fecha_inicio + timedelta(minutes=servicio.duracion_minutos)

    # -------- Servicio de día completo --------
    if servicio.ocupa_dia_completo:
        otras = Consulta.objects.filter(
            estado__in=ESTADOS_ACTIVOS,
            fecha__date=fecha_inicio.date(),
        )
        if consulta_id:
            otras = otras.exclude(pk=consulta_id)
        if otras.exists():
            errores.append(
                'Este servicio ocupa todo el día. Solo se puede agendar '
                'si el día está completamente libre.'
            )
        return errores

    # -------- Solapamiento --------
    solapadas = Consulta.objects.filter(
        estado__in=ESTADOS_ACTIVOS,
        fecha__lt=fecha_fin,
        fecha_fin__gt=fecha_inicio,
    )
    if consulta_id:
        solapadas = solapadas.exclude(pk=consulta_id)
    if solapadas.exists():
        errores.append('La franja elegida se solapa con otra consulta.')

    # -------- Almuerzo (nunca, salvo día completo ya excluido) --------
    almuerzo_ini = _aware(datetime.combine(fecha_inicio.date(), time(HORA_ALMUERZO_INICIO, 0)))
    almuerzo_fin = _aware(datetime.combine(fecha_inicio.date(), time(HORA_ALMUERZO_FIN, 0)))
    if fecha_inicio < almuerzo_fin and fecha_fin > almuerzo_ini:
        errores.append('No se pueden agendar consultas entre las 12:00 y las 13:00 (almuerzo).')

    # -------- Fecha bloqueada --------
    seccion = 'manana' if fecha_inicio.hour < HORA_ALMUERZO_INICIO else 'tarde'
    if fecha_bloqueada(fecha_inicio.date(), seccion):
        errores.append('Esta franja está bloqueada para consultas.')

    if es_admin:
        return errores

    # -------- Reglas del paciente --------
    if not servicio.agendable_web:
        errores.append(f'El servicio «{servicio.nombre}» se agenda únicamente vía WhatsApp.')

    if fecha_inicio.weekday() not in DIAS_PERMITIDOS:
        errores.append('Solo se puede agendar de martes a sábado.')

    if fecha_inicio < ahora + timedelta(hours=HORAS_MINIMAS_ANTELACION):
        errores.append(f'Debe agendar con al menos {HORAS_MINIMAS_ANTELACION} horas de antelación.')

    activas = paciente.consultas.filter(estado__in=ESTADOS_ACTIVOS)
    if consulta_id:
        activas = activas.exclude(pk=consulta_id)
    if activas.exists():
        errores.append('Ya tiene una consulta activa. Debe completarla antes de agendar otra.')

    desde = ahora - timedelta(days=DIAS_ENTRE_CONSULTAS)
    recientes = paciente.consultas.filter(creado__gte=desde).exclude(estado='cancelada')
    if consulta_id:
        recientes = recientes.exclude(pk=consulta_id)
    if recientes.exists():
        errores.append(f'Debe esperar al menos {DIAS_ENTRE_CONSULTAS} días entre consultas.')

    return errores


# ---------------------------------------------------------------------
# Comprobaciones tempranas
# ---------------------------------------------------------------------
def puede_agendar(paciente):
    ahora = timezone.now()
    if paciente.consultas.filter(estado__in=ESTADOS_ACTIVOS).exists():
        return False, 'Ya tiene una consulta activa. Debe completarla antes de agendar otra.'
    desde = ahora - timedelta(days=DIAS_ENTRE_CONSULTAS)
    if paciente.consultas.filter(creado__gte=desde).exclude(estado='cancelada').exists():
        return False, f'Debe esperar al menos {DIAS_ENTRE_CONSULTAS} días entre consultas.'
    return True, None


def puede_cancelar(consulta):
    if consulta.estado == 'cancelada':
        return False, 'Esta consulta ya está cancelada.'
    if consulta.estado == 'realizada':
        return False, 'No se puede cancelar una consulta ya realizada.'
    if consulta.fecha < timezone.now():
        return False, 'No se puede cancelar una consulta pasada.'
    return True, None


def puede_marcar_realizada(consulta):
    """Solo se exige tratamiento. La medicación es opcional."""
    if not (consulta.tratamiento or '').strip():
        return False, ['tratamiento']
    return True, []


def paciente_tiene_datos_clinicos(paciente):
    faltan = []
    if not (paciente.alergias or '').strip():
        faltan.append('alergias')
    if not (paciente.medicacion or '').strip():
        faltan.append('medicación')
    if not (paciente.pais or '').strip():
        faltan.append('país')
    if faltan:
        return False, (
            'Antes de agendar debe completar sus datos clínicos: '
            + ', '.join(faltan) + '.'
        )
    return True, None


# ---------------------------------------------------------------------
# Etiquetas
# ---------------------------------------------------------------------
DIAS_ES = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
MESES_ES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']


def etiqueta_dia(dia):
    return f'{DIAS_ES[dia.weekday()]} {dia.day} de {MESES_ES[dia.month - 1]}'