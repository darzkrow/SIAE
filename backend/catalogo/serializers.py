from rest_framework import serializers
from core.serializers import SoftDeleteSerializer
from .models import CategoriaProducto, Marca


class CategoriaProductoSerializer(SoftDeleteSerializer):
    """Serializer para CategoriaProducto con soft delete"""
    class Meta(SoftDeleteSerializer.Meta):
        model = CategoriaProducto
        fields = SoftDeleteSerializer.Meta.fields + ['nombre', 'descripcion']
        read_only_fields = SoftDeleteSerializer.Meta.read_only_fields


class MarcaSerializer(SoftDeleteSerializer):
    """Serializer para Marca con soft delete"""
    class Meta(SoftDeleteSerializer.Meta):
        model = Marca
        fields = SoftDeleteSerializer.Meta.fields + ['nombre', 'descripcion']
        read_only_fields = SoftDeleteSerializer.Meta.read_only_fields
