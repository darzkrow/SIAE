"""
🎮 ViewSets Base Reutilizables - Por Morris

ViewSets que otros pueden heredar para tener funcionalidad común.
¡Como tener controles de juego predefinidos! 🕹️
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    🏗️ ViewSet Base con Funcionalidad Común
    
    Incluye CRUD básico y manejo de errores consistente.
    """
    def get_serializer_context(self):
        """Agregar contexto adicional al serializer"""
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def perform_create(self, serializer):
        """Guardar con usuario actual si el modelo lo soporta"""
        if hasattr(serializer.Meta.model, 'created_by'):
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()

    def perform_update(self, serializer):
        """Actualizar con usuario actual si el modelo lo soporta"""
        if hasattr(serializer.Meta.model, 'updated_by'):
            serializer.save(updated_by=self.request.user)
        else:
            serializer.save()


class SoftDeleteViewSet(BaseModelViewSet):
    """
    🗑️ ViewSet con Soft Delete
    
    En lugar de borrar de verdad, marca como eliminado.
    """
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restaurar un registro eliminado"""
        obj = self.get_object()
        if hasattr(obj, 'restore'):
            obj.restore()
            serializer = self.get_serializer(obj)
            return Response(serializer.data)
        return Response(
            {'error': 'Este modelo no soporta restauración'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def perform_destroy(self, instance):
        """Soft delete en lugar de delete real"""
        if hasattr(instance, 'soft_delete'):
            instance.soft_delete()
        else:
            instance.delete()

    @action(detail=False, methods=['get'])
    def deleted(self, request):
        """Listar registros eliminados"""
        if hasattr(self.get_queryset().model, 'all_objects'):
            queryset = self.get_queryset().model.all_objects.filter(
                deleted_at__isnull=False
            )
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response(
            {'error': 'Este modelo no soporta soft delete'},
            status=status.HTTP_400_BAD_REQUEST
        )
