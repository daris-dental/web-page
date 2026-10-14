from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import Usuario


class Command(BaseCommand):
    help = 'Elimina cuentas sin verificar de más de 24 horas.'

    def handle(self, *args, **options):
        limite = timezone.now() - timedelta(hours=24)
        qs = Usuario.objects.filter(
            email_verificado=False,
            fecha_registro__lt=limite,
        )
        n = qs.count()
        qs.delete()
        self.stdout.write(self.style.SUCCESS(f'{n} cuentas eliminadas.'))