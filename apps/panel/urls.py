from django.urls import path

from apps.services import views_admin as sv
from apps.patients import views_admin as pv
from apps.consultations import views_admin as cv
from . import views

app_name = 'panel'

urlpatterns = [
    path('', views.home, name='home'),

    # Servicios
    path('servicios/', sv.lista, name='servicios_lista'),
    path('servicios/crear/', sv.crear, name='servicios_crear'),
    path('servicios/<int:pk>/editar/', sv.editar, name='servicios_editar'),
    path('servicios/<int:pk>/eliminar/', sv.eliminar, name='servicios_eliminar'),

    # Pacientes
    path('pacientes/', pv.lista, name='pacientes_lista'),
    path('pacientes/<int:pk>/', pv.detalle, name='pacientes_detalle'),
    path('pacientes/<int:pk>/editar/', pv.editar, name='pacientes_editar'),

    # Consultas
    path('consultas/', cv.lista, name='consultas_lista'),
    path('consultas/crear/', cv.crear, name='consultas_crear'),
    path('consultas/detalles/<int:pk>/<int:ck>', cv.detalle, name='consultas_detalles'),
    path('consultas/<int:pk>/editar/', cv.editar, name='consultas_editar'),
    path('consultas/<int:pk>/confirmar/', cv.marcar_confirmada, name='consultas_confirmar'),
    path('consultas/<int:pk>/realizada/', cv.marcar_realizada, name='consultas_marcar_realizada'),
    path('consultas/<int:pk>/realizada/', cv.marcar_realizada, name='consultas_marcar_realizada'),
    path('consultas/<int:pk>/eliminar/', cv.eliminar, name='consultas_eliminar'),
    path('consultas/eliminar-masivo/', cv.eliminar_masivo, name='consultas_eliminar_masivo'),
    path('consultas/<int:pk>/estado/<str:estado>/', cv.marcar_estado, name='consultas_estado'),

    # Días bloqueados
    
    path('fechas-bloqueadas/', cv.fechas_bloqueadas, name='fechas_bloqueadas'),
    path('fechas-bloqueadas/<int:pk>/desbloquear/', cv.desbloquear_fecha, name='desbloquear_fecha'),
        # Imágenes de consulta
    path('consultas/<int:pk>/imagenes/subir/', cv.subir_imagen, name='consultas_subir_imagen',),
    path('imagenes/<int:pk>/eliminar/', cv.eliminar_imagen, name='consultas_eliminar_imagen',),

        # Artículos
    path('articulos/', sv.articulos_lista, name='articulos_lista'),
    path('articulos/crear/', sv.articulos_crear, name='articulos_crear'),
    path('articulos/<int:pk>/editar/', sv.articulos_editar, name='articulos_editar'),
    path('articulos/<int:pk>/eliminar/', sv.articulos_eliminar, name='articulos_eliminar'),
]