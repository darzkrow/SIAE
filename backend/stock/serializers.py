from rest_framework import serializers
from core.serializers import BaseModelSerializer
from stock.models import Stock, MovimientoInventario, InventoryAudit

class StockSerializer(BaseModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    ubicacion_nombre = serializers.CharField(source='ubicacion.nombre', read_only=True)
    
    class Meta(BaseModelSerializer.Meta):
        model = Stock
        fields = BaseModelSerializer.Meta.fields + [
            'content_type', 'object_id', 'producto', 'producto_nombre',
            'ubicacion', 'ubicacion_nombre', 'cantidad', 'lote', 
            'fecha_vencimiento', 'estado_operativo'
        ]

class MovimientoInventarioSerializer(BaseModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    ubicacion_origen_nombre = serializers.CharField(source='ubicacion_origen.nombre', read_only=True)
    ubicacion_destino_nombre = serializers.CharField(source='ubicacion_destino.nombre', read_only=True)
    
    class Meta(BaseModelSerializer.Meta):
        model = MovimientoInventario
        fields = BaseModelSerializer.Meta.fields + [
            'content_type', 'object_id', 'producto', 'producto_nombre',
            'ubicacion_origen', 'ubicacion_origen_nombre',
            'ubicacion_destino', 'ubicacion_destino_nombre',
            'tipo_movimiento', 'status', 'cantidad', 'fecha_movimiento',
            'razon', 'creado_por', 'aprobado_por'
        ]

class InventoryAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryAudit
        fields = '__all__'
