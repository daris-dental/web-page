from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'      # ruta real del paquete
    label = 'accounts'          # nombre corto que usarás en todo el proyecto