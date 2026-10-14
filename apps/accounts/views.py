from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import CreateView
import uuid
from .forms import RegistroUsuarioForm, LoginForm, CambiarPasswordForm


class RegistroView(CreateView):
    form_class = RegistroUsuarioForm
    template_name = 'accounts/registro.html'
    success_url = '/'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.email_verificado = False
        user.token_verificacion = uuid.uuid4()
        user.save()

        # Crear el Paciente asociado
        from apps.patients.models import Paciente
        Paciente.objects.get_or_create(usuario=user)

        # Enviar correo de verificación
        self._enviar_verificacion(self.request, user)

        messages.info(
            self.request,
            'Le enviamos un correo de verificación. '
            'Debe confirmarlo antes de iniciar sesión.'
        )
        return super().form_valid(form)

    def _enviar_verificacion(self, request, user):
        from django.urls import reverse
        from django.core.mail import send_mail
        from django.conf import settings
        import logging

        logger = logging.getLogger(__name__)

        token_url = reverse('accounts:verificar_email', args=[str(user.token_verificacion)])
        url_completa = request.build_absolute_uri(token_url)

        asunto = "Verifica tu cuenta — Dari's Dental"
        mensaje = (
            f"Hola {user.get_full_name() or user.username},\n\n"
            f"Gracias por registrarte en Dari's Dental.\n"
            f"Para activar tu cuenta, haz clic en este enlace:\n\n"
            f"{url_completa}\n\n"
            f"Si no te registraste, ignora este correo.\n"
            f"Las cuentas sin verificar se eliminan después de 24 horas."
        )

        try:
            send_mail(
                asunto, mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            # No rompemos el registro si falla el correo
            logger.exception('Error al enviar correo de verificación a %s: %s', user.email, e)

        if settings.DEBUG:
            print('\n' + '=' * 60)
            print('CORREO DE VERIFICACIÓN (modo DEBUG)')
            print(f'Para: {user.email}')
            print(f'Enlace: {url_completa}')
            print('=' * 60 + '\n')

    def form_invalid(self, form):
        import sys
        print('\n' + '=' * 60, file=sys.stderr)
        print('FORM INVÁLIDO', file=sys.stderr)
        print('Errores:', dict(form.errors), file=sys.stderr)
        print('Datos POST:', dict(self.request.POST), file=sys.stderr)
        print('=' * 60 + '\n', file=sys.stderr)
        return super().form_invalid(form)


def verificar_email(request, token):
    from django.shortcuts import render, get_object_or_404
    from .models import Usuario

    try:
        user = Usuario.objects.get(token_verificacion=token)
    except Usuario.DoesNotExist:
        return render(request, 'accounts/verificar_invalido.html')

    if user.email_verificado:
        return render(request, 'accounts/verificar_ok.html')

    user.email_verificado = True
    user.save(update_fields=['email_verificado'])

    # Login automático
    login(request, user, backend='apps.accounts.backends.EmailOrUsernameBackend')
    return render(request, 'accounts/verificar_ok.html')


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Usuario o contraseña incorrectos, o correo no verificado.'
        )
        return super().form_invalid(form)


class CustomPasswordChangeView(PasswordChangeView):
    form_class = CambiarPasswordForm
    template_name = 'accounts/cambiar_password.html'
    success_url = reverse_lazy('patients:perfil')


@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')