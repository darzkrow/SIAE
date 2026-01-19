from rest_framework import serializers
from .models import OrdenCompra, ItemOrden, Correlativo

class ItemOrdenSerializer(serializers.ModelSerializer):
    producto_str = serializers.SerializerMethodField()
    product_type_read = serializers.SerializerMethodField()
    product_id_read = serializers.SerializerMethodField()
    # write-only fields for creating generic relation
    product_type = serializers.CharField(write_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ItemOrden
        fields = ['id', 'product_type', 'product_id', 'product_type_read', 'product_id_read', 'producto_str', 'cantidad_pedida', 'cantidad_recibida', 'precio_estimado']
    
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

class OrdenCompraSerializer(serializers.ModelSerializer):
    items = ItemOrdenSerializer(many=True, read_only=True)
    solicitante_nombre = serializers.SerializerMethodField()
    aprobador_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = OrdenCompra
        fields = [
            'id', 'codigo', 'movimiento', 'fecha_creacion', 
            'solicitante', 'solicitante_nombre', 'aprobador', 'aprobador_nombre',
            'status', 'notas', 'items'
        ]
        read_only_fields = ['id', 'codigo', 'fecha_creacion']

    def get_solicitante_nombre(self, obj):
        return obj.solicitante.username if obj.solicitante else None

    def get_aprobador_nombre(self, obj):
        return obj.aprobador.username if obj.aprobador else None
