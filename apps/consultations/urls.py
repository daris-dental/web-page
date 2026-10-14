from django.urls import path
from . import views

app_name = 'consultations'

urlpatterns = [
    path('', views.mis_consultas, name='mis_consultas'),
    path('agendar/', views.agendar, name='agendar'),
    path('disponibilidad/<int:servicio_id>/', views.disponibilidad_servicio, name='disponibilidad'),
    path('<int:pk>/', views.detalle, name='detalle'),
    path('<int:pk>/cancelar/', views.cancelar, name='cancelar'),
]