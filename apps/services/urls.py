from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.lista_servicios, name='lista'),
    path('inicio/', views.landing, name='inicio'),
]