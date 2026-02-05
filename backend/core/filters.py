from django.db.models import Q, F
from django.contrib.postgres.search import SearchQuery, SearchRank
from django_filters import rest_framework as filters
from rest_framework import filters as drf_filters
import re
import logging

logger = logging.getLogger(__name__)

class AdvancedSearchFilter(drf_filters.BaseFilterBackend):
    """
    Advanced search filter that supports complex query syntax and full-text search.
    """
    search_param = 'search'
    
    def filter_queryset(self, request, queryset, view):
        search_query = request.query_params.get(self.search_param, '').strip()
        if not search_query:
            return queryset
        
        search_fields = getattr(view, 'search_fields', [])
        if not search_fields:
            return queryset
        
        try:
            if hasattr(queryset.model, 'search_vector'):
                return self._apply_fulltext_search(queryset, search_query)
            return self._apply_simple_search(queryset, search_query, search_fields)
        except Exception as e:
            logger.error(f"Error in advanced search: {e}")
            return self._apply_simple_search(queryset, search_query, search_fields)

    def _apply_fulltext_search(self, queryset, search_query):
        search_query_obj = SearchQuery(search_query, config='spanish')
        return queryset.filter(search_vector=search_query_obj).annotate(
            rank=SearchRank(F('search_vector'), search_query_obj)
        ).order_by('-rank')

    def _apply_simple_search(self, queryset, search_query, search_fields):
        search_q = Q()
        for field in search_fields:
            search_q |= Q(**{f"{field}__icontains": search_query})
        return queryset.filter(search_q)

class FacetedSearchFilter(filters.FilterSet):
    """
    Base class for faceted search and filtering.
    """
    created_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        fields = []

class ProductFilterSet(filters.FilterSet):
    """Filtro avanzado para todos los productos."""
    stock_min = filters.NumberFilter(field_name='stock_actual', lookup_expr='gte')
    stock_max = filters.NumberFilter(field_name='stock_actual', lookup_expr='lte')
    precio_min = filters.NumberFilter(field_name='precio_unitario', lookup_expr='gte')
    precio_max = filters.NumberFilter(field_name='precio_unitario', lookup_expr='lte')
    creado_despues = filters.DateTimeFilter(field_name='creado_en', lookup_expr='gte')
    creado_antes = filters.DateTimeFilter(field_name='creado_en', lookup_expr='lte')

    class Meta:
        fields = [
            'tipo_inventario', 'es_critico', 'nivel_criticidad', 
            'proveedor', 'categoria', 'activo'
        ]
