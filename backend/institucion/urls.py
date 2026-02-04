"""
URL Configuration for Hidroven Organizational Restructuring API.
Provides both new hierarchical API endpoints and backward compatibility.
"""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from . import views

# Create router for API endpoints
router = DefaultRouter()

# ============================================================================
# NEW HIERARCHICAL API ENDPOINTS
# ============================================================================

# Organizational hierarchy endpoints
router.register(r'empresas', views.EmpresaViewSet, basename='empresa')
router.register(r'vicepresidencias', views.VicepresidenciaViewSet, basename='vicepresidencia')
router.register(r'unidades-organizacionales', views.UnidadOrganizacionalViewSet, basename='unidad-organizacional')
router.register(r'almacenes-regionales', views.AlmacenRegionalViewSet, basename='almacen-regional')

# Asset tracking endpoints
# router.register(r'activos', views.ActivoInventarioViewSet, basename='activo')
# router.register(r'historial-movimientos', views.HistorialMovimientoActivoViewSet, basename='historial-movimiento')

# Transfer workflow endpoints
# router.register(r'solicitudes-traslado', views.SolicitudTrasladoViewSet, basename='solicitud-traslado')

# Migration monitoring endpoints
router.register(r'migraciones', views.MigracionOrganizacionalViewSet, basename='migracion')

# ============================================================================
# BACKWARD COMPATIBILITY API ENDPOINTS
# ============================================================================

# Legacy organizational endpoints (maintain exact same URLs)
router.register(r'organizaciones-centrales', views.OrganizacionCentralViewSet, basename='organizacion-central')
router.register(r'sucursales', views.SucursalViewSet, basename='sucursal')
router.register(r'acueductos', views.AcueductoViewSet, basename='acueducto')

# ============================================================================
# URL PATTERNS
# ============================================================================

urlpatterns = [
    # Include all router URLs
    path('api/institucion/', include(router.urls)),
    
    # Additional custom endpoints can be added here
    # path('api/institucion/custom-endpoint/', views.custom_view, name='custom-endpoint'),
]

# For backward compatibility, also expose endpoints at root level
# This maintains compatibility with existing frontend code
legacy_router = DefaultRouter()
legacy_router.register(r'organizaciones', views.OrganizacionCentralViewSet, basename='organizacion-legacy')
legacy_router.register(r'sucursales', views.SucursalViewSet, basename='sucursal-legacy')
legacy_router.register(r'acueductos', views.AcueductoViewSet, basename='acueducto-legacy')

urlpatterns += [
    # Legacy endpoints at root level for backward compatibility
    path('api/', include(legacy_router.urls)),
]