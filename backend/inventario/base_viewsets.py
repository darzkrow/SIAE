"""
Base API ViewSets with common functionality for the GSIH system.

This module provides enhanced base viewsets that include:
- Pagination, filtering, and permissions
- Bulk operations (create, update, delete)
- Advanced search and filtering
- Audit trail integration
- Performance optimizations
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from typing import List, Dict, Any, Optional
import json
from django.utils import timezone

from auditoria.mixins import AuditMixin, TrashBinMixin
from inventario.permissions import IsAdminOrReadOnly


class CustomPagination:
    """Custom pagination configuration for API responses."""
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class BaseAPIViewSet(AuditMixin, TrashBinMixin, viewsets.ModelViewSet):
    """
    Enhanced base viewset with common functionality for all API endpoints.
    
    Features:
    - Standard pagination, filtering, and permissions
    - Bulk operations (create, update, delete)
    - Advanced search capabilities
    - Audit trail integration
    - Performance optimizations
    - Error handling
    """
    
    # Default configuration
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
    # Override in subclasses
    search_fields = []
    filterset_fields = []
    ordering_fields = []
    ordering = ['id']
    
    def get_queryset(self):
        """
        Apply dynamic filtering and permissions to queryset.
        Override in subclasses for custom filtering logic.
        """
        queryset = super().get_queryset()
        return self.apply_user_permissions(queryset)
    
    def apply_user_permissions(self, queryset):
        """
        Apply user-specific permissions to filter queryset.
        Override in subclasses for custom permission logic.
        """
        user = self.request.user
        
        # Admin users see everything
        if hasattr(user, 'role') and user.role == 'ADMIN':
            return queryset
        
        # Apply default filtering based on user's organization
        if hasattr(user, 'sucursal') and user.sucursal:
            # Try to filter by sucursal if the model has this relationship
            if hasattr(queryset.model, 'sucursal'):
                return queryset.filter(sucursal=user.sucursal)
            elif hasattr(queryset.model, 'ubicacion'):
                # For stock models that have ubicacion -> acueducto -> sucursal
                return queryset.filter(ubicacion__acueducto__sucursal=user.sucursal)
        
        return queryset
    
    def perform_create(self, serializer):
        """Enhanced create with audit trail."""
        # Set created_by if the model has this field
        if hasattr(serializer.Meta.model, 'created_by'):
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        """Enhanced update with audit trail."""
        # Set updated_by if the model has this field
        if hasattr(serializer.Meta.model, 'updated_by'):
            serializer.save(updated_by=self.request.user)
        else:
            serializer.save()
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Bulk creation endpoint.
        
        Expected payload:
        {
            "items": [
                {"field1": "value1", "field2": "value2"},
                {"field1": "value3", "field2": "value4"}
            ]
        }
        """
        items_data = request.data.get('items', [])
        
        if not items_data:
            return Response(
                {'error': 'No items provided for bulk creation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(items_data) > 100:
            return Response(
                {'error': 'Maximum 100 items allowed per bulk operation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_items = []
        errors = []
        
        with transaction.atomic():
            for i, item_data in enumerate(items_data):
                try:
                    serializer = self.get_serializer(data=item_data)
                    if serializer.is_valid():
                        self.perform_create(serializer)
                        created_items.append(serializer.data)
                    else:
                        errors.append({
                            'index': i,
                            'data': item_data,
                            'errors': serializer.errors
                        })
                except Exception as e:
                    errors.append({
                        'index': i,
                        'data': item_data,
                        'errors': str(e)
                    })
        
        response_data = {
            'created_count': len(created_items),
            'error_count': len(errors),
            'created_items': created_items
        }
        
        if errors:
            response_data['errors'] = errors
            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['patch'])
    def bulk_update(self, request):
        """
        Bulk update endpoint.
        
        Expected payload:
        {
            "updates": [
                {"id": 1, "field1": "new_value1"},
                {"id": 2, "field2": "new_value2"}
            ]
        }
        """
        updates_data = request.data.get('updates', [])
        
        if not updates_data:
            return Response(
                {'error': 'No updates provided for bulk operation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(updates_data) > 100:
            return Response(
                {'error': 'Maximum 100 items allowed per bulk operation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_items = []
        errors = []
        
        with transaction.atomic():
            for i, update_data in enumerate(updates_data):
                try:
                    item_id = update_data.pop('id', None)
                    if not item_id:
                        errors.append({
                            'index': i,
                            'data': update_data,
                            'errors': 'ID is required for updates'
                        })
                        continue
                    
                    try:
                        instance = self.get_queryset().get(id=item_id)
                    except self.queryset.model.DoesNotExist:
                        errors.append({
                            'index': i,
                            'data': update_data,
                            'errors': f'Object with ID {item_id} not found'
                        })
                        continue
                    
                    serializer = self.get_serializer(instance, data=update_data, partial=True)
                    if serializer.is_valid():
                        self.perform_update(serializer)
                        updated_items.append(serializer.data)
                    else:
                        errors.append({
                            'index': i,
                            'data': update_data,
                            'errors': serializer.errors
                        })
                        
                except Exception as e:
                    errors.append({
                        'index': i,
                        'data': update_data,
                        'errors': str(e)
                    })
        
        response_data = {
            'updated_count': len(updated_items),
            'error_count': len(errors),
            'updated_items': updated_items
        }
        
        if errors:
            response_data['errors'] = errors
            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        """
        Bulk delete endpoint.
        
        Expected payload:
        {
            "ids": [1, 2, 3, 4, 5]
        }
        """
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response(
                {'error': 'No IDs provided for bulk deletion'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(ids) > 100:
            return Response(
                {'error': 'Maximum 100 items allowed per bulk operation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count = 0
        errors = []
        
        with transaction.atomic():
            for item_id in ids:
                try:
                    instance = self.get_queryset().get(id=item_id)
                    self.perform_destroy(instance)
                    deleted_count += 1
                except self.queryset.model.DoesNotExist:
                    errors.append({
                        'id': item_id,
                        'error': f'Object with ID {item_id} not found'
                    })
                except Exception as e:
                    errors.append({
                        'id': item_id,
                        'error': str(e)
                    })
        
        response_data = {
            'deleted_count': deleted_count,
            'error_count': len(errors)
        }
        
        if errors:
            response_data['errors'] = errors
            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def advanced_search(self, request):
        """
        Advanced search endpoint with complex filtering.
        
        Query parameters:
        - q: Text search across search_fields
        - filters: JSON object with field filters
        - date_range: JSON object with date range filters
        - ordering: Field name for ordering (prefix with - for desc)
        """
        queryset = self.get_queryset()
        
        # Text search
        search_query = request.query_params.get('q', '').strip()
        if search_query and self.search_fields:
            search_filter = Q()
            for field in self.search_fields:
                search_filter |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(search_filter)
        
        # Advanced filters
        filters_param = request.query_params.get('filters', '{}')
        try:
            filters = json.loads(filters_param)
            for field, value in filters.items():
                if hasattr(queryset.model, field.split('__')[0]):
                    queryset = queryset.filter(**{field: value})
        except json.JSONDecodeError:
            return Response(
                {'error': 'Invalid JSON in filters parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Date range filters
        date_range_param = request.query_params.get('date_range', '{}')
        try:
            date_range = json.loads(date_range_param)
            for field, range_data in date_range.items():
                if 'start' in range_data:
                    queryset = queryset.filter(**{f"{field}__gte": range_data['start']})
                if 'end' in range_data:
                    queryset = queryset.filter(**{f"{field}__lte": range_data['end']})
        except json.JSONDecodeError:
            return Response(
                {'error': 'Invalid JSON in date_range parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Custom ordering
        ordering = request.query_params.get('ordering')
        if ordering and ordering.lstrip('-') in self.ordering_fields:
            queryset = queryset.order_by(ordering)
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def export_data(self, request):
        """
        Export data in various formats.
        
        Query parameters:
        - format: 'json', 'csv' (default: json)
        - fields: Comma-separated list of fields to include
        """
        export_format = request.query_params.get('format', 'json').lower()
        fields = request.query_params.get('fields', '').split(',') if request.query_params.get('fields') else None
        
        queryset = self.filter_queryset(self.get_queryset())
        
        if export_format == 'json':
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            
            if fields:
                # Filter fields if specified
                filtered_data = []
                for item in data:
                    filtered_item = {field: item.get(field) for field in fields if field in item}
                    filtered_data.append(filtered_item)
                data = filtered_data
            
            return Response({
                'count': len(data),
                'data': data,
                'exported_at': timezone.now().isoformat()
            })
        
        elif export_format == 'csv':
            import csv
            from django.http import HttpResponse
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{self.queryset.model._meta.model_name}_export.csv"'
            
            if not queryset.exists():
                return response
            
            # Get field names
            serializer = self.get_serializer(queryset.first())
            field_names = fields or list(serializer.data.keys())
            
            writer = csv.DictWriter(response, fieldnames=field_names)
            writer.writeheader()
            
            for obj in queryset:
                serializer = self.get_serializer(obj)
                row_data = {field: serializer.data.get(field, '') for field in field_names}
                writer.writerow(row_data)
            
            return response
        
        else:
            return Response(
                {'error': f'Unsupported export format: {export_format}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def field_choices(self, request):
        """
        Get available choices for model fields.
        Useful for building dynamic forms and filters.
        """
        model = self.queryset.model
        choices_data = {}
        
        for field in model._meta.fields:
            if field.choices:
                choices_data[field.name] = [
                    {'value': choice[0], 'label': choice[1]}
                    for choice in field.choices
                ]
        
        return Response(choices_data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get basic statistics for the model.
        Override in subclasses for custom statistics.
        """
        from django.db.models import Count, Avg, Sum, Min, Max
        
        queryset = self.filter_queryset(self.get_queryset())
        
        stats = {
            'total_count': queryset.count(),
        }
        
        # Add numeric field statistics
        for field in self.queryset.model._meta.fields:
            if field.get_internal_type() in ['IntegerField', 'FloatField', 'DecimalField']:
                field_stats = queryset.aggregate(
                    avg=Avg(field.name),
                    sum=Sum(field.name),
                    min=Min(field.name),
                    max=Max(field.name)
                )
                stats[f'{field.name}_stats'] = field_stats
        
        return Response(stats)


class ReadOnlyBaseAPIViewSet(BaseAPIViewSet):
    """
    Read-only version of BaseAPIViewSet for models that should not be modified via API.
    """
    
    def create(self, request, *args, **kwargs):
        return Response(
            {'error': 'Create operation not allowed'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def update(self, request, *args, **kwargs):
        return Response(
            {'error': 'Update operation not allowed'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def partial_update(self, request, *args, **kwargs):
        return Response(
            {'error': 'Update operation not allowed'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, *args, **kwargs):
        return Response(
            {'error': 'Delete operation not allowed'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    # Disable bulk operations
    def bulk_create(self, request):
        return Response(
            {'error': 'Bulk create operation not allowed'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def bulk_update(self, request):
        return Response(
            {'error': 'Bulk update operation not allowed'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def bulk_delete(self, request):
        return Response(
            {'error': 'Bulk delete operation not allowed'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )