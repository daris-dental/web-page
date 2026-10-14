from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Datos extra', {'fields': ('telefono', 'fecha_nacimiento')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Datos extra', {
            'fields': ('email', 'first_name', 'last_name', 'telefono', 'fecha_nacimiento')
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'telefono', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')