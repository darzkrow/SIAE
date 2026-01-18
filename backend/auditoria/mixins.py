from rest_framework.decorators import action
from rest_framework.response import Response
from .utils import log_action

class AuditMixin:
    """
    Mixin para ViewSets que registra automáticamente las acciones de CREATE, UPDATE y DELETE.
    """
    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(instance, 'CREATE')

    def perform_update(self, serializer):
        instance = serializer.save()
        # Aquí se podría implementar una lógica para detectar cambios específicos
        log_action(instance, 'UPDATE')

    def perform_destroy(self, instance):
        # Si el modelo tiene deleted_at, es un SOFT_DELETE
        action = 'DELETE' if hasattr(instance, 'deleted_at') else 'HARD_DELETE'
        log_action(instance, action)
        instance.delete()

class TrashBinMixin:
    """
    Mixin para ver objetos eliminados (papelera).
    """
    @action(detail=False, methods=['get'], url_path='papelera')
    def papelera(self, request):
        if not hasattr(self.queryset.model, 'deleted_at'):
            return Response({"error": "Este modelo no soporta papelera"}, status=400)
        
        # Usar all_objects o filtrar los que tienen deleted_at
        queryset = self.queryset.model.all_objects.filter(deleted_at__isnull=False)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='restaurar')
    def restaurar(self, request, pk=None):
        instance = self.queryset.model.all_objects.get(pk=pk)
        instance.restore()
        log_action(instance, 'RESTORE')
        return Response({"status": "Objeto restaurado"})
