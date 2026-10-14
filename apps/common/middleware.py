import time
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse


class SessionIdleTimeoutMiddleware:
    """
    Cierra la sesión si el usuario lleva más de SESSION_COOKIE_AGE segundos
    sin actividad. Diferencia de la expiración nativa de Django en que:
      - Hace un logout explícito (limpia la sesión).
      - Redirige al login con un mensaje de aviso.
      - No cuenta como "actividad" las peticiones a /static ni /media.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout = settings.SESSION_COOKIE_AGE

    def __call__(self, request):
        if request.user.is_authenticated:
            now = time.time()
            last = request.session.get('last_activity')

            if last and (now - last) > self.timeout:
                logout(request)
                login_url = reverse('accounts:login')
                return redirect(f'{login_url}?expirada=1')

            request.session['last_activity'] = now

        return self.get_response(request)