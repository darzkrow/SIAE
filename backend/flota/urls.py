"""
Flota URLs - Fleet Management API Routes
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tipos', views.TipoVehiculoViewSet, basename='tipo-vehiculo')
router.register(r'vehiculos', views.VehiculoViewSet, basename='vehiculo')
router.register(r'documentos', views.DocumentoVehiculoViewSet, basename='documento-vehiculo')
router.register(r'mantenimientos', views.MantenimientoVehiculoViewSet, basename='mantenimiento-vehiculo')
router.register(r'asignaciones', views.AsignacionVehiculoViewSet, basename='asignacion-vehiculo')
router.register(r'combustible', views.RegistroCombustibleViewSet, basename='registro-combustible')

urlpatterns = [
    path('', include(router.urls)),
]
