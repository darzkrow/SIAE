"""
Advanced Search and Filtering System for GSIH API endpoints.

This module provides comprehensive search and filtering capabilities including:
- Full-text search across multiple fields
- Complex query syntax support
- Faceted search and filtering
- Search result ranking and highlighting
- Performance optimizations
"""

from django.db.models import Q, F, Value, CharField, Case, When
from django.db.models.functions import Concat, Lower
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django_filters import rest_framework as filters
from rest_framework import filters as drf_filters
from typing import Dict, List, Optional, Any
import re
import json
import logging

logger = logging.getLogger(__name__)


class AdvancedSearchFilter(drf_filters.BaseFilterBackend):
    """
    Advanced search filter that supports complex query syntax and full-text search.
    
    Features:
    - Full-text search with PostgreSQL search vectors
    - Complex query syntax (AND, OR, NOT, quotes, wildcards)
    - Field-specific search (field:value)
    - Range queries (field:min..max)
    - Fuzzy matching and typo tolerance
    """
    
    search_param = 'search'
    search_title = 'Search'
    search_description = 'A search term for advanced text search'
    
    def filter_queryset(self, request, queryset, view):
        """
        Apply advanced search filtering to the queryset.
        """
        search_query = request.query_params.get(self.search_param, '').strip()
        
        if not search_query:
            return queryset
        
        # Get search fields from view
        search_fields = getattr(view, 'search_fields', [])
        if not search_fields:
            return queryset
        
        try:
            # Parse and apply search query
            return self._apply_advanced_search(queryset, search_query, search_fields)
        except Exception as e:
            logger.error(f"Error in advanced search: {e}")
            # Fallback to simple search
            return self._apply_simple_search(queryset, search_query, search_fields)
    
    def _apply_advanced_search(self, queryset, search_query, search_fields):
        """
        Apply advanced search with complex query parsing.
        """
        # Check if PostgreSQL full-text search is available
        if self._has_search_vector_field(queryset.model):
            return self._apply_fulltext_search(queryset, search_query)
        
        # Parse complex query syntax
        parsed_query = self._parse_search_query(search_query)
        
        # Build Q object from parsed query
        search_q = self._build_search_q(parsed_query, search_fields)
        
        if search_q:
            return queryset.filter(search_q)
        
        return queryset
    
    def _has_search_vector_field(self, model):
        """
        Check if model has a search_vector field for full-text search.
        """
        return hasattr(model, '_meta') and any(
            field.name == 'search_vector' 
            for field in model._meta.fields
        )
    
    def _apply_fulltext_search(self, queryset, search_query):
        """
        Apply PostgreSQL full-text search using search vectors.
        """
        try:
            # Create search query
            search_query_obj = SearchQuery(search_query, config='spanish')
            
            # Filter and rank results
            return queryset.filter(
                search_vector=search_query_obj
            ).annotate(
                rank=SearchRank(F('search_vector'), search_query_obj)
            ).order_by('-rank')
            
        except Exception as e:
            logger.error(f"Full-text search error: {e}")
            # Fallback to simple search
            return self._apply_simple_search(queryset, search_query, ['nombre', 'descripcion'])
    
    def _parse_search_query(self, query):
        """
        Parse complex search query syntax.
        
        Supported syntax:
        - "exact phrase" - exact phrase search
        - field:value - field-specific search
        - field:min..max - range search
        - +required -excluded - required/excluded terms
        - term1 AND term2 - boolean AND
        - term1 OR term2 - boolean OR
        - NOT term - negation
        """
        parsed = {
            'terms': [],
            'phrases': [],
            'field_searches': {},
            'range_searches': {},
            'required_terms': [],
            'excluded_terms': [],
            'boolean_operations': []
        }
        
        # Extract quoted phrases
        phrase_pattern = r'"([^"]*)"'
        phrases = re.findall(phrase_pattern, query)
        parsed['phrases'] = phrases
        query = re.sub(phrase_pattern, '', query)
        
        # Extract field-specific searches
        field_pattern = r'(\w+):([^\s]+)'
        field_matches = re.findall(field_pattern, query)
        for field, value in field_matches:
            if '..' in value:
                # Range search
                try:
                    min_val, max_val = value.split('..')
                    parsed['range_searches'][field] = {
                        'min': min_val.strip(),
                        'max': max_val.strip()
                    }
                except ValueError:
                    parsed['field_searches'][field] = value
            else:
                parsed['field_searches'][field] = value
        
        query = re.sub(field_pattern, '', query)
        
        # Extract required/excluded terms
        required_pattern = r'\+(\w+)'
        excluded_pattern = r'-(\w+)'
        
        required_terms = re.findall(required_pattern, query)
        excluded_terms = re.findall(excluded_pattern, query)
        
        parsed['required_terms'] = required_terms
        parsed['excluded_terms'] = excluded_terms
        
        query = re.sub(required_pattern, '', query)
        query = re.sub(excluded_pattern, '', query)
        
        # Extract boolean operations
        boolean_pattern = r'(\w+)\s+(AND|OR|NOT)\s+(\w+)'
        boolean_matches = re.findall(boolean_pattern, query, re.IGNORECASE)
        parsed['boolean_operations'] = boolean_matches
        
        # Remove boolean operators from query
        query = re.sub(r'\s+(AND|OR|NOT)\s+', ' ', query, flags=re.IGNORECASE)
        
        # Remaining terms
        terms = [term.strip() for term in query.split() if term.strip()]
        parsed['terms'] = terms
        
        return parsed
    
    def _build_search_q(self, parsed_query, search_fields):
        """
        Build Django Q object from parsed search query.
        """
        q_objects = []
        
        # Handle phrases
        for phrase in parsed_query['phrases']:
            phrase_q = Q()
            for field in search_fields:
                phrase_q |= Q(**{f"{field}__icontains": phrase})
            q_objects.append(phrase_q)
        
        # Handle regular terms
        for term in parsed_query['terms']:
            term_q = Q()
            for field in search_fields:
                term_q |= Q(**{f"{field}__icontains": term})
            q_objects.append(term_q)
        
        # Handle required terms
        for term in parsed_query['required_terms']:
            term_q = Q()
            for field in search_fields:
                term_q |= Q(**{f"{field}__icontains": term})
            q_objects.append(term_q)
        
        # Handle field-specific searches
        for field, value in parsed_query['field_searches'].items():
            if field in [f.split('__')[0] for f in search_fields]:
                q_objects.append(Q(**{f"{field}__icontains": value}))
        
        # Handle range searches
        for field, range_data in parsed_query['range_searches'].items():
            if field in [f.split('__')[0] for f in search_fields]:
                range_q = Q()
                if range_data['min']:
                    range_q &= Q(**{f"{field}__gte": range_data['min']})
                if range_data['max']:
                    range_q &= Q(**{f"{field}__lte": range_data['max']})
                q_objects.append(range_q)
        
        # Combine all Q objects
        if not q_objects:
            return Q()
        
        final_q = q_objects[0]
        for q_obj in q_objects[1:]:
            final_q &= q_obj
        
        # Handle excluded terms
        for term in parsed_query['excluded_terms']:
            exclude_q = Q()
            for field in search_fields:
                exclude_q |= Q(**{f"{field}__icontains": term})
            final_q &= ~exclude_q
        
        return final_q
    
    def _apply_simple_search(self, queryset, search_query, search_fields):
        """
        Fallback simple search implementation.
        """
        search_q = Q()
        for field in search_fields:
            search_q |= Q(**{f"{field}__icontains": search_query})
        
        return queryset.filter(search_q)


class FacetedSearchFilter(filters.FilterSet):
    """
    Base class for faceted search and filtering.
    
    Provides:
    - Multiple filter options
    - Range filters
    - Choice filters
    - Date range filters
    """
    
    # Date range filter
    created_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    # Numeric range filters
    price_min = filters.NumberFilter(field_name='precio_unitario', lookup_expr='gte')
    price_max = filters.NumberFilter(field_name='precio_unitario', lookup_expr='lte')
    
    stock_min = filters.NumberFilter(field_name='stock_actual', lookup_expr='gte')
    stock_max = filters.NumberFilter(field_name='stock_actual', lookup_expr='lte')
    
    # Boolean filters
    is_active = filters.BooleanFilter(field_name='activo')
    
    # Multiple choice filter
    categories = filters.ModelMultipleChoiceFilter(
        field_name='categoria',
        queryset=None,  # Set in subclasses
        conjoined=False  # OR logic
    )
    
    class Meta:
        fields = []


class InventorySearchFilter(FacetedSearchFilter):
    """
    Specialized search filter for inventory items.
    """
    
    # Inventory-specific filters
    low_stock = filters.BooleanFilter(method='filter_low_stock')
    expiring_soon = filters.BooleanFilter(method='filter_expiring_soon')
    dangerous = filters.BooleanFilter(field_name='es_peligroso')
    
    def filter_low_stock(self, queryset, name, value):
        """Filter items with stock below minimum."""
        if value:
            return queryset.filter(stock_actual__lte=F('stock_minimo'))
        return queryset
    
    def filter_expiring_soon(self, queryset, name, value):
        """Filter items expiring within 30 days."""
        if value:
            from datetime import timedelta
            from django.utils import timezone
            
            expiry_date = timezone.now().date() + timedelta(days=30)
            return queryset.filter(
                fecha_caducidad__lte=expiry_date,
                fecha_caducidad__gte=timezone.now().date()
            )
        return queryset


class SearchResultHighlighter:
    """
    Utility class for highlighting search terms in results.
    """
    
    @staticmethod
    def highlight_text(text, search_terms, highlight_class='highlight'):
        """
        Highlight search terms in text.
        """
        if not text or not search_terms:
            return text
        
        highlighted_text = str(text)
        
        for term in search_terms:
            if len(term) < 2:  # Skip very short terms
                continue
            
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            highlighted_text = pattern.sub(
                f'<span class="{highlight_class}">{term}</span>',
                highlighted_text
            )
        
        return highlighted_text
    
    @staticmethod
    def extract_snippets(text, search_terms, snippet_length=150):
        """
        Extract relevant snippets from text containing search terms.
        """
        if not text or not search_terms:
            return text[:snippet_length] + '...' if len(text) > snippet_length else text
        
        text = str(text)
        snippets = []
        
        for term in search_terms:
            if len(term) < 2:
                continue
            
            # Find term positions
            positions = []
            start = 0
            while True:
                pos = text.lower().find(term.lower(), start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            
            # Extract snippets around term positions
            for pos in positions:
                start = max(0, pos - snippet_length // 2)
                end = min(len(text), pos + len(term) + snippet_length // 2)
                snippet = text[start:end]
                
                if start > 0:
                    snippet = '...' + snippet
                if end < len(text):
                    snippet = snippet + '...'
                
                snippets.append(snippet)
        
        return snippets[0] if snippets else (
            text[:snippet_length] + '...' if len(text) > snippet_length else text
        )


class SearchAnalytics:
    """
    Analytics and metrics for search functionality.
    """
    
    @staticmethod
    def log_search_query(user, query, results_count, execution_time=None):
        """
        Log search query for analytics.
        """
        try:
            from auditoria.models import AuditLog
            from django.contrib.contenttypes.models import ContentType
            
            # Log search query
            AuditLog.objects.create(
                user=user,
                action='search',
                content_type=ContentType.objects.get_for_model(user),
                object_id=user.id,
                object_repr=f"Search: {query}",
                changes={
                    'query': query,
                    'results_count': results_count,
                    'execution_time': execution_time
                }
            )
        except Exception as e:
            logger.error(f"Error logging search query: {e}")
    
    @staticmethod
    def get_popular_searches(days=30, limit=10):
        """
        Get most popular search queries.
        """
        try:
            from auditoria.models import AuditLog
            from django.utils import timezone
            from datetime import timedelta
            from django.db.models import Count
            
            since_date = timezone.now() - timedelta(days=days)
            
            popular_searches = AuditLog.objects.filter(
                action='search',
                timestamp__gte=since_date
            ).values(
                'changes__query'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:limit]
            
            return [
                {
                    'query': item['changes__query'],
                    'count': item['count']
                }
                for item in popular_searches
                if item['changes__query']
            ]
            
        except Exception as e:
            logger.error(f"Error getting popular searches: {e}")
            return []