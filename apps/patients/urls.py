from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('perfil/', views.perfil, name='perfil'),
    path('datos/', views.paciente_form, name='paciente_form'),
]