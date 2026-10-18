from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from apps.services import views as services_views
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cuentas/', include('apps.accounts.urls')),
    path('pacientes/', include('apps.patients.urls')),
    path('servicios/', include('apps.services.urls')),
    path('consultas/', include('apps.consultations.urls')),
    path('panel/', include('apps.panel.urls')),
    path('', services_views.landing, name='landing'),
    path('privacidad/', TemplateView.as_view(template_name='privacidad.html'), name='privacidad'),
    path('terminos/', TemplateView.as_view(template_name='terminos.html'), name='terminos'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)