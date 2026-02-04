from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .utils import log_action, log_data_operation

class AuditMixin:
    """
    Mixin para ViewSets que registra automáticamente las acciones de CREATE, UPDATE y DELETE.
    Enhanced to support the new audit logging features.
    """
    def perform_create(self, serializer):
        instance = serializer.save()
        # Enhanced logging with risk assessment
        risk_level = self.get_audit_risk_level('CREATE', instance)
        extra_data = self.get_audit_extra_data('CREATE', instance, serializer)
        log_action(instance, 'CREATE', risk_level=risk_level, extra_data=extra_data)

    def perform_update(self, serializer):
        # Capture old values before saving
        old_instance = self.get_object()
        old_values = self.get_field_values(old_instance, serializer.validated_data.keys())
        
        instance = serializer.save()
        
        # Capture new values and create changes dict
        new_values = self.get_field_values(instance, serializer.validated_data.keys())
        changes = {
            'old_values': old_values,
            'new_values': new_values,
            'fields_changed': list(serializer.validated_data.keys())
        }
        
        risk_level = self.get_audit_risk_level('UPDATE', instance)
        extra_data = self.get_audit_extra_data('UPDATE', instance, serializer)
        log_action(instance, 'UPDATE', changes=changes, risk_level=risk_level, extra_data=extra_data)

    def perform_destroy(self, instance):
        # Capture instance data before deletion
        extra_data = self.get_audit_extra_data('DELETE', instance)
        
        # Si el modelo tiene deleted_at, es un SOFT_DELETE
        action = 'DELETE' if hasattr(instance, 'deleted_at') else 'HARD_DELETE'
        risk_level = self.get_audit_risk_level(action, instance)
        
        log_action(instance, action, risk_level=risk_level, extra_data=extra_data)
        instance.delete()
    
    def get_audit_risk_level(self, action, instance):
        """
        Determine the risk level for an audit action.
        Override this method in subclasses for custom risk assessment.
        """
        if action in ['DELETE', 'HARD_DELETE']:
            return 'MEDIUM'
        elif action == 'UPDATE':
            # Check if sensitive fields are being modified
            sensitive_fields = getattr(self, 'audit_sensitive_fields', [])
            if hasattr(self, 'request') and self.request.data:
                modified_fields = set(self.request.data.keys())
                if any(field in sensitive_fields for field in modified_fields):
                    return 'HIGH'
            return 'LOW'
        else:  # CREATE
            return 'LOW'
    
    def get_audit_extra_data(self, action, instance, serializer=None):
        """
        Get additional data to include in audit logs.
        Override this method in subclasses for custom extra data.
        """
        extra_data = {
            'model': instance._meta.label,
            'action_source': 'api'
        }
        
        if hasattr(self, 'request'):
            extra_data['endpoint'] = self.request.path
            extra_data['method'] = self.request.method
        
        if serializer and hasattr(serializer, 'validated_data'):
            extra_data['fields_modified'] = list(serializer.validated_data.keys())
        
        return extra_data
    
    def get_field_values(self, instance, field_names):
        """
        Extract field values from an instance.
        """
        values = {}
        for field_name in field_names:
            if hasattr(instance, field_name):
                value = getattr(instance, field_name)
                # Convert non-serializable values to strings
                if hasattr(value, 'pk'):  # Foreign key
                    values[field_name] = str(value)
                elif hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
                    values[field_name] = list(value) if hasattr(value, 'all') else str(value)
                else:
                    values[field_name] = value
        return values

class TrashBinMixin:
    """
    Mixin para ver objetos eliminados (papelera).
    Enhanced with better audit logging.
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
        
        # Enhanced audit logging for restore action
        extra_data = {
            'model': instance._meta.label,
            'action_source': 'api',
            'endpoint': request.path,
            'method': request.method,
            'restored_from_trash': True
        }
        
        log_action(instance, 'RESTORE', risk_level='MEDIUM', extra_data=extra_data)
        return Response({"status": "Objeto restaurado"})

class BulkOperationMixin:
    """
    Mixin for handling bulk operations with comprehensive audit logging.
    """
    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """Bulk delete operation with audit logging"""
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "No IDs provided"}, status=400)
        
        queryset = self.get_queryset().filter(id__in=ids)
        count = queryset.count()
        
        # Log the bulk operation
        log_data_operation(
            user=request.user,
            action='BULK_DELETE',
            affected_count=count,
            operation_type=f'{self.queryset.model._meta.label}_bulk_delete',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            extra_data={
                'model': self.queryset.model._meta.label,
                'endpoint': request.path,
                'ids': ids
            }
        )
        
        # Perform the deletion
        if hasattr(self.queryset.model, 'deleted_at'):
            # Soft delete
            queryset.update(deleted_at=timezone.now())
        else:
            # Hard delete
            queryset.delete()
        
        return Response({
            "status": "success",
            "deleted_count": count,
            "message": f"Successfully deleted {count} items"
        })
    
    @action(detail=False, methods=['patch'], url_path='bulk-update')
    def bulk_update(self, request):
        """Bulk update operation with audit logging"""
        ids = request.data.get('ids', [])
        update_data = request.data.get('data', {})
        
        if not ids or not update_data:
            return Response({"error": "IDs and update data required"}, status=400)
        
        queryset = self.get_queryset().filter(id__in=ids)
        count = queryset.count()
        
        # Log the bulk operation
        log_data_operation(
            user=request.user,
            action='BULK_UPDATE',
            affected_count=count,
            operation_type=f'{self.queryset.model._meta.label}_bulk_update',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            extra_data={
                'model': self.queryset.model._meta.label,
                'endpoint': request.path,
                'ids': ids,
                'update_fields': list(update_data.keys())
            }
        )
        
        # Perform the update
        updated_count = queryset.update(**update_data)
        
        return Response({
            "status": "success",
            "updated_count": updated_count,
            "message": f"Successfully updated {updated_count} items"
        })
    
    def get_client_ip(self, request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
