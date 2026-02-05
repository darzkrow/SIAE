from rest_framework import serializers
from core.serializers import SoftDeleteSerializer
from .models import OrdenCompra, ItemOrden, Correlativo


class ItemOrdenSerializer(SoftDeleteSerializer):
    """Serializer para ItemOrden con soft delete y lógica de generic relation"""
    producto_str = serializers.SerializerMethodField()
    product_type_read = serializers.SerializerMethodField()
    product_id_read = serializers.SerializerMethodField()
    # write-only fields for creating generic relation
    product_type = serializers.CharField(write_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta(SoftDeleteSerializer.Meta):
        model = ItemOrden
        fields = SoftDeleteSerializer.Meta.fields + [
            'product_type', 'product_id', 'product_type_read', 'product_id_read', 
            'producto_str', 'cantidad_pedida', 'cantidad_recibida', 'precio_estimado'
        ]
        read_only_fields = SoftDeleteSerializer.Meta.read_only_fields
    
    def get_producto_str(self, obj):
        return str(obj.producto)

    def get_product_type_read(self, obj):
        if obj.content_type:
            return obj.content_type.model
        return None

    def get_product_id_read(self, obj):
        return obj.object_id

    def create(self, validated_data):
        product_type = validated_data.pop('product_type')
        product_id = validated_data.pop('product_id')
        from django.contrib.contenttypes.models import ContentType
        type_map = {
            'chemical': 'chemicalproduct',
            'pipe': 'pipe',
            'pump': 'pumpandmotor',
            'accessory': 'accessory'
        }
        if product_type not in type_map:
            raise serializers.ValidationError({'product_type': 'Tipo inválido'})
        try:
            ct = ContentType.objects.get(app_label='inventario', model=type_map[product_type])
        except ContentType.DoesNotExist:
            raise serializers.ValidationError({'product_type': 'ContentType no encontrado'})
        validated_data['content_type'] = ct
        validated_data['object_id'] = product_id
        if not ct.get_all_objects_for_this_type().filter(id=product_id).exists():
            raise serializers.ValidationError({'product_id': f'El producto con ID {product_id} no existe para el tipo {product_type}'})
        return super().create(validated_data)

class OrdenCompraSerializer(SoftDeleteSerializer):
    """Serializer para OrdenCompra con soft delete y workflow"""
    items = ItemOrdenSerializer(many=True, read_only=True)
    solicitante_nombre = serializers.SerializerMethodField()
    
    # Workflow fields
    aprobado_comercializacion_nombre = serializers.SerializerMethodField()
    aprobado_presupuesto_nombre = serializers.SerializerMethodField()
    aprobado_finanzas_nombre = serializers.SerializerMethodField()
    ejecutado_compras_nombre = serializers.SerializerMethodField()
    
    class Meta(SoftDeleteSerializer.Meta):
        model = OrdenCompra
        fields = SoftDeleteSerializer.Meta.fields + [
            'codigo', 'tipo', 'parent_order', 'movimiento', 
            'fecha_creacion', 'solicitante', 'solicitante_nombre',
            'aprobado_comercializacion_por', 'aprobado_comercializacion_nombre', 'fecha_aprobacion_comercializacion',
            'aprobado_presupuesto_por', 'aprobado_presupuesto_nombre', 'fecha_aprobacion_presupuesto',
            'aprobado_finanzas_por', 'aprobado_finanzas_nombre', 'fecha_aprobacion_finanzas',
            'ejecutado_compras_por', 'ejecutado_compras_nombre', 'fecha_ejecucion_compras',
            'status', 'notas', 'motivo_cancelacion', 'items'
        ]
        read_only_fields = SoftDeleteSerializer.Meta.read_only_fields + [
            'codigo', 'fecha_creacion', 
            'aprobado_comercializacion_por', 'fecha_aprobacion_comercializacion',
            'aprobado_presupuesto_por', 'fecha_aprobacion_presupuesto',
            'aprobado_finanzas_por', 'fecha_aprobacion_finanzas',
            'ejecutado_compras_por', 'fecha_ejecucion_compras'
        ]

    def get_solicitante_nombre(self, obj):
        return obj.solicitante.username if obj.solicitante else None

    def get_aprobado_comercializacion_nombre(self, obj):
        return obj.aprobado_comercializacion_por.username if obj.aprobado_comercializacion_por else None

    def get_aprobado_presupuesto_nombre(self, obj):
        return obj.aprobado_presupuesto_por.username if obj.aprobado_presupuesto_por else None

    def get_aprobado_finanzas_nombre(self, obj):
        return obj.aprobado_finanzas_por.username if obj.aprobado_finanzas_por else None

    def get_ejecutado_compras_nombre(self, obj):
        return obj.ejecutado_compras_por.username if obj.ejecutado_compras_por else None

class ConsolidacionSerializer(serializers.Serializer):
    """Serializer para la acción de consolidar órdenes"""
    ordenes_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Lista de IDs de órdenes individuales a consolidar"
    )
