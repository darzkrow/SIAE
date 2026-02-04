"""
Serializers para Subalmacén
"""

from rest_framework import serializers
from core.serializers import BaseModelSerializer
from institucion.models import Subalmacen


class SubalmacenSerializer(BaseModelSerializer):
    """Serializer para Subalmacén con información geográfica"""
    
    ubicacion_completa = serializers.CharField(
        source='get_ubicacion_completa',
        read_only=True
    )
    estado_nombre = serializers.CharField(
        source='estado.name',
        read_only=True
    )
    municipio_nombre = serializers.CharField(
        source='municipio.name',
        read_only=True,
        allow_null=True
    )
    parroquia_nombre = serializers.CharField(
        source='parroquia.name',
        read_only=True,
        allow_null=True
    )
    sucursal_nombre = serializers.CharField(
        source='sucursal.nombre',
        read_only=True
    )
    responsable_nombre = serializers.SerializerMethodField()
    coordenadas_dict = serializers.SerializerMethodField()
    
    class Meta:
        model = Subalmacen
        fields = BaseModelSerializer.Meta.fields + [
            'nombre', 'codigo', 'sucursal', 'sucursal_nombre',
            'estado', 'estado_nombre',
            'municipio', 'municipio_nombre',
            'parroquia', 'parroquia_nombre',
            'direccion', 'coordenadas_gps', 'coordenadas_dict',
            'responsable', 'responsable_nombre',
            'capacidad', 'activo', 'descripcion',
            'ubicacion_completa',
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_responsable_nombre(self, obj):
        if obj.responsable:
            return obj.responsable.get_full_name() or obj.responsable.username
        return None
    
    def get_coordenadas_dict(self, obj):
        if obj.coordenadas_gps:
            try:
                lat, lng = obj.coordenadas_gps.split(',')
                return {
                    'lat': float(lat.strip()),
                    'lng': float(lng.strip())
                }
            except (ValueError, AttributeError):
                return None
        return None
