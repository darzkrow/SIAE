"""
🎮 ViewSets Base Reutilizables - Por Morris

ViewSets que otros pueden heredar para tener funcionalidad común.
¡Como tener controles de juego predefinidos! 🕹️
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone


from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters
from rest_framework.permissions import IsAuthenticated

from auditoria.mixins import AuditMixin, TrashBinMixin

class BaseModelViewSet(viewsets.ModelViewSet):
    """
    🏗️ ViewSet Base con Funcionalidad Común
    """
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def perform_create(self, serializer):
        if hasattr(serializer.Meta.model, 'created_by'):
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()

    def perform_update(self, serializer):
        if hasattr(serializer.Meta.model, 'updated_by'):
            serializer.save(updated_by=self.request.user)
        else:
            serializer.save()


class SoftDeleteViewSet(BaseModelViewSet):
    """
    🗑️ ViewSet con Soft Delete
    """
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        obj = self.get_object()
        if hasattr(obj, 'restore'):
            obj.restore()
            serializer = self.get_serializer(obj)
            return Response(serializer.data)
        return Response({'error': 'No soporta restauración'}, status=400)

    def perform_destroy(self, instance):
        if hasattr(instance, 'soft_delete'):
            instance.soft_delete()
        else:
            instance.delete()

    @action(detail=False, methods=['get'])
    def deleted(self, request):
        if hasattr(self.get_queryset().model, 'all_objects'):
            queryset = self.get_queryset().model.all_objects.filter(deleted_at__isnull=False)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response({'error': 'No soporta soft delete'}, status=400)


class BaseAPIViewSet(AuditMixin, TrashBinMixin, SoftDeleteViewSet):
    """
    🚀 ViewSet Base de Alto Nivel
    Centraliza filtrado, búsqueda avanzada y auditoría.
    """
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filtro de seguridad por sucursal si aplica
        if hasattr(user, 'role') and user.role != 'ADMIN' and hasattr(user, 'sucursal'):
            if hasattr(queryset.model, 'sucursal'):
                queryset = queryset.filter(sucursal=user.sucursal)
            elif hasattr(queryset.model, 'ubicacion'):
                queryset = queryset.filter(
                    Q(ubicacion__subalmacen__sucursal=user.sucursal) |
                    Q(ubicacion__almacen_regional__sucursal=user.sucursal) |
                    Q(ubicacion__acueducto__sucursal=user.sucursal)
                ).distinct()
        return queryset
