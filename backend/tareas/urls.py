"""
Tareas URLs - Task Scheduling Module API Routes
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categorias', views.CategoriaTareaViewSet, basename='categoria-tarea')
router.register(r'columnas', views.ColumnaKanbanViewSet, basename='columna-kanban')
router.register(r'', views.TareaViewSet, basename='tarea')
router.register(r'asignaciones', views.AsignacionTareaViewSet, basename='asignacion-tarea')
router.register(r'comentarios', views.ComentarioTareaViewSet, basename='comentario-tarea')
router.register(r'archivos', views.ArchivoAdjuntoViewSet, basename='archivo-adjunto')
router.register(r'recordatorios', views.RecordatorioTareaViewSet, basename='recordatorio-tarea')

urlpatterns = [
    path('', include(router.urls)),
]
