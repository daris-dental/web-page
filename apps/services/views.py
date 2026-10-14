from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render
from .models import Servicio, Articulo
from django.conf import settings


def lista_servicios(request):
    servicios = Servicio.objects.filter(activo=True)
    return render(request, 'services/lista.html', {'servicios': servicios})



@never_cache
def landing(request):
    """Página pública. Visible para anónimos y usuarios logueados."""
    servicios = (
        Servicio.objects
        .filter(activo=True)
        .order_by('nombre')
    )

    # Mensaje de WhatsApp cuando el usuario está logueado
    wa_text_servicio = ''
    if request.user.is_authenticated:
        u = request.user
        wa_text_servicio = (
            f"Hola, soy {u.get_full_name() or u.username} "
            f"(usuario: {u.username}). "
            f"Me interesa el servicio de "
        )

    return render(request, 'landing.html', {
        'servicios': servicios,
        'whatsapp_number': getattr(settings, 'WHATSAPP_NUMBER', '5354783902'),
        'wa_text_servicio': wa_text_servicio,
    })

@never_cache
def landing(request):
    servicios = Servicio.objects.filter(activo=True).order_by('nombre')
    articulos = Articulo.objects.filter(activo=True).order_by('nombre')

    wa_text_servicio = ''
    wa_text_articulo = ''
    if request.user.is_authenticated:
        u = request.user
        base = f"Hola, soy {u.get_full_name() or u.username} (usuario: {u.username}). "
        wa_text_servicio = base + "Me interesa el servicio de "
        wa_text_articulo = base + "Quiero comprar "

    return render(request, 'landing.html', {
        'servicios': servicios,
        'articulos': articulos,
        'whatsapp_number': getattr(settings, 'WHATSAPP_NUMBER', '5354783902'),
        'wa_text_servicio': wa_text_servicio,
        'wa_text_articulo': wa_text_articulo,
    })