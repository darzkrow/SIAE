"""
Serializers for Hidroven Organizational Restructuring API.
Provides both new hierarchical API endpoints and backward compatibility.
"""
from rest_framework import serializers
from core.serializers import BaseModelSerializer
from django.contrib.auth import get_user_model
from .models import (
    Subalmacen,
    # New hierarchical models
    Empresa, Vicepresidencia, UnidadOrganizacional, AlmacenRegional,
    MigracionOrganizacional,
    # Legacy models for backward compatibility
    OrganizacionCentral, Sucursal, Acueducto
)

User = get_user_model()


# ============================================================================
# NEW HIERARCHICAL API SERIALIZERS
# ============================================================================

class EmpresaSerializer(BaseModelSerializer):
    """Serializer for Empresa (root company) model."""
    
    subsidiarias_count = serializers.SerializerMethodField()
    vicepresidencias_count = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = Empresa
        fields = BaseModelSerializer.Meta.fields + [
            'nombre', 'codigo', 'rif', 'direccion', 'telefono', 'email',
            'activo', 'fecha_creacion', 'fecha_actualizacion', 'parent',
            'subsidiarias_count', 'vicepresidencias_count', 'full_path'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ['fecha_creacion', 'fecha_actualizacion']
    
    def get_subsidiarias_count(self, obj):
        """Get count of subsidiary companies."""
        return obj.subsidiarias.count()
    
    def get_vicepresidencias_count(self, obj):
        """Get count of vicepresidencias under this company."""
        return obj.vicepresidencias.count()
    
    def get_full_path(self, obj):
        """Get full hierarchical path."""
        return obj.get_full_path()


class VicepresidenciaSerializer(BaseModelSerializer):
    """Serializer for Vicepresidencia model."""
    
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    responsable_username = serializers.CharField(source='responsable.username', read_only=True)
    unidades_count = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = Vicepresidencia
        fields = BaseModelSerializer.Meta.fields + [
            'empresa', 'empresa_nombre', 'nombre', 'codigo', 'tipo',
            'descripcion', 'responsable', 'responsable_username', 'activo',
            'fecha_creacion', 'fecha_actualizacion', 'parent',
            'unidades_count', 'full_path'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ['fecha_creacion', 'fecha_actualizacion']
    
    def get_unidades_count(self, obj):
        """Get count of organizational units under this VP."""
        return obj.unidades_organizacionales.count()
    
    def get_full_path(self, obj):
        """Get full hierarchical path."""
        return obj.get_full_path()


class UnidadOrganizacionalSerializer(BaseModelSerializer):
    """Serializer for UnidadOrganizacional model."""
    
    vicepresidencia_nombre = serializers.CharField(source='vicepresidencia.nombre', read_only=True)
    empresa_nombre = serializers.CharField(source='vicepresidencia.empresa.nombre', read_only=True)
    responsable_username = serializers.CharField(source='responsable.username', read_only=True)
    almacenes_count = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = UnidadOrganizacional
        fields = BaseModelSerializer.Meta.fields + [
            'vicepresidencia', 'vicepresidencia_nombre', 'empresa_nombre',
            'nombre', 'codigo', 'tipo', 'descripcion', 'ubicacion',
            'responsable', 'responsable_username', 'activo',
            'fecha_creacion', 'fecha_actualizacion', 'parent',
            'almacenes_count', 'full_path'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ['fecha_creacion', 'fecha_actualizacion']
    
    def get_almacenes_count(self, obj):
        """Get count of regional warehouses under this unit."""
        return obj.almacenes_regionales.count()
    
    def get_full_path(self, obj):
        """Get full hierarchical path."""
        return obj.get_full_path()


class AlmacenRegionalSerializer(BaseModelSerializer):
    """Serializer for AlmacenRegional model."""
    
    unidad_nombre = serializers.CharField(source='unidad_organizacional.nombre', read_only=True)
    vicepresidencia_nombre = serializers.CharField(source='unidad_organizacional.vicepresidencia.nombre', read_only=True)
    manager_username = serializers.CharField(source='manager.username', read_only=True)
    activos_count = serializers.SerializerMethodField()
    capacity_usage = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = AlmacenRegional
        fields = BaseModelSerializer.Meta.fields + [
            'unidad_organizacional', 'unidad_nombre', 'vicepresidencia_nombre',
            'nombre', 'prefijo', 'ubicacion', 'manager', 'manager_username',
            'capacidad_maxima', 'activo', 'fecha_creacion', 'fecha_actualizacion',
            'descripcion', 'telefono', 'email', 'activos_count', 'capacity_usage',
            'full_path'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ['fecha_creacion', 'fecha_actualizacion']
    
    def get_activos_count(self, obj):
        """Get count of assets currently in this warehouse."""
        # This will now refer to the related_name in the new app's model
        # or we might need to handle it via a service if cross-app access is restricted.
        # For now, Django should handle it if the models are registered.
        try:
            return obj.activos_actuales.count()
        except:
            return 0
    
    def get_capacity_usage(self, obj):
        """Get current capacity usage percentage."""
        return obj.get_current_capacity_usage()
    
    def get_full_path(self, obj):
        """Get full hierarchical path."""
        return obj.get_full_path()


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


class MigracionOrganizacionalSerializer(BaseModelSerializer):
    """Serializer for MigracionOrganizacional model."""
    
    migrado_por_username = serializers.CharField(source='migrado_por.username', read_only=True)
    validado_por_username = serializers.CharField(source='validado_por.username', read_only=True)
    revertido_por_username = serializers.CharField(source='revertido_por.username', read_only=True)
    old_reference_display = serializers.SerializerMethodField()
    new_reference_display = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = MigracionOrganizacional
        fields = BaseModelSerializer.Meta.fields + [
            'organizacion_central_id', 'sucursal_id', 'acueducto_id',
            'empresa', 'vicepresidencia', 'unidad_organizacional', 'acueducto_nuevo',
            'fecha_migracion', 'estado_migracion', 'validado', 'migrado_por',
            'migrado_por_username', 'validado_por', 'validado_por_username',
            'fecha_validacion', 'datos_originales', 'puede_revertir',
            'fecha_reversion', 'revertido_por', 'revertido_por_username',
            'notas', 'errores', 'warnings', 'fecha_actualizacion',
            'old_reference_display', 'new_reference_display'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + [
            'fecha_migracion', 'fecha_actualizacion', 'old_reference_display',
            'new_reference_display'
        ]
    
    def get_old_reference_display(self, obj):
        """Get display name for old structure reference."""
        return obj.get_old_reference_display()
    
    def get_new_reference_display(self, obj):
        """Get display name for new structure reference."""
        return obj.get_new_reference_display()


# ============================================================================
# BACKWARD COMPATIBILITY SERIALIZERS
# ============================================================================

class OrganizacionCentralSerializer(BaseModelSerializer):
    """Backward compatibility serializer for OrganizacionCentral."""
    
    sucursales_count = serializers.SerializerMethodField()
    parent_nombre = serializers.CharField(source='parent.nombre', read_only=True)
    
    class Meta(BaseModelSerializer.Meta):
        model = OrganizacionCentral
        fields = BaseModelSerializer.Meta.fields + [
            'nombre', 'rif', 'parent', 'parent_nombre', 'sucursales_count'
        ]
    
    def get_sucursales_count(self, obj):
        """Get count of sucursales under this organization."""
        return obj.sucursales.count()


class SucursalSerializer(BaseModelSerializer):
    """Backward compatibility serializer for Sucursal."""
    
    organizacion_nombre = serializers.CharField(source='organizacion_central.nombre', read_only=True)
    acueductos_count = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = Sucursal
        fields = BaseModelSerializer.Meta.fields + [
            'nombre', 'organizacion_central', 'organizacion_nombre',
            'codigo', 'direccion', 'telefono', 'acueductos_count'
        ]
    
    def get_acueductos_count(self, obj):
        """Get count of acueductos under this sucursal."""
        return obj.acueductos.count()


class AcueductoSerializer(BaseModelSerializer):
    """Backward compatibility serializer for Acueducto."""
    
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    organizacion_nombre = serializers.CharField(source='sucursal.organizacion_central.nombre', read_only=True)
    
    class Meta(BaseModelSerializer.Meta):
        model = Acueducto
        fields = BaseModelSerializer.Meta.fields + [
            'nombre', 'sucursal', 'sucursal_nombre', 'organizacion_nombre',
            'codigo', 'ubicacion'
        ]


# ============================================================================
# HIERARCHY TREE SERIALIZER
# ============================================================================

class HierarchyTreeSerializer(BaseModelSerializer):
    """Serializer for hierarchical tree representation."""
    
    children = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = Empresa  # Can be used for any MPTT model
        fields = BaseModelSerializer.Meta.fields + ['nombre', 'codigo', 'level', 'children']
    
    def get_children(self, obj):
        """Get immediate children in hierarchy."""
        if hasattr(obj, 'get_children'):
            children = obj.get_children()
            return self.__class__(children, many=True, context=self.context).data
        return []
    
    def get_level(self, obj):
        """Get hierarchy level."""
        return getattr(obj, 'level', 0)