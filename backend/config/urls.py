"""URL Configuration with API documentation."""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.views.generic.base import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

def health_check(request):
    return HttpResponse("OK", status=200)

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    
    # API endpoints
    path('api/accounts/', include('accounts.urls')),
    path('api/catalog/', include('catalogo.urls')),
    path('api/compras/', include('compras.urls')),
    path('api/auditoria/', include('auditoria.urls')),
    path('api/notificaciones/', include('notificaciones.urls')),
    path('api/', include('inventario.urls')),
    
    # API Documentation (OpenAPI/Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
