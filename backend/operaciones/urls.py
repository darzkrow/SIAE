"""
URL Configuration for Operaciones API.
Handles asset tracking, transfer workflows, and audit trails.
"""
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()

# Asset tracking and transfer endpoints
router.register(r'activos', views.ActivoInventarioViewSet, basename='activo')
router.register(r'solicitudes-traslado', views.SolicitudTrasladoViewSet, basename='solicitud-traslado')
router.register(r'historial-movimientos', views.HistorialMovimientoActivoViewSet, basename='historial-movimiento')

# Audit trail endpoints
router.register(r'auditoria/estados', views.AuditoriaEstadoActivoViewSet, basename='auditoria-estado')
router.register(r'auditoria/aprobaciones', views.AuditoriaAprobacionViewSet, basename='auditoria-aprobacion')
router.register(r'auditoria/operaciones', views.AuditoriaOperacionSistemaViewSet, basename='auditoria-operacion')
router.register(r'auditoria/accesos', views.AuditoriaAccesoSistemaViewSet, basename='auditoria-acceso')

urlpatterns = [
    path('', include(router.urls)),
]
