from rest_framework import serializers
from .models import Notificacion, Alerta

class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = '__all__'

class AlertaSerializer(serializers.ModelSerializer):
    producto_str = serializers.SerializerMethodField()
    product_type_read = serializers.SerializerMethodField()
    product_id_read = serializers.SerializerMethodField()
    # write-only fields to create generic relation
    product_type = serializers.CharField(write_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Alerta
        fields = ['id', 'product_type', 'product_id', 'product_type_read', 'product_id_read', 'producto_str', 'acueducto', 'umbral_minimo', 'activo']
        read_only_fields = ['id', 'producto_str']

    def get_producto_str(self, obj):
        return str(obj.producto) if obj.producto else "N/A"

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
