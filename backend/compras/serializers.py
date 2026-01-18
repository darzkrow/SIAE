from rest_framework import serializers
from .models import OrdenCompra, ItemOrden, Correlativo

class ItemOrdenSerializer(serializers.ModelSerializer):
    producto_str = serializers.SerializerMethodField()
    
    class Meta:
        model = ItemOrden
        fields = ['id', 'producto', 'producto_str', 'cantidad_pedida', 'cantidad_recibida', 'precio_estimado']
    
    def get_producto_str(self, obj):
        return str(obj.producto)

class OrdenCompraSerializer(serializers.ModelSerializer):
    items = ItemOrdenSerializer(many=True, read_only=True)
    solicitante_nombre = serializers.CharField(source='solicitante.username', read_only=True)
    aprobador_nombre = serializers.CharField(source='aprobador.username', read_only=True)
    
    class Meta:
        model = OrdenCompra
        fields = [
            'id', 'codigo', 'movimiento', 'fecha_creacion', 
            'solicitante', 'solicitante_nombre', 'aprobador', 'aprobador_nombre',
            'status', 'notas', 'items'
        ]
        read_only_fields = ['id', 'codigo', 'fecha_creacion']
