from rest_framework import serializers
from .models import Notificacion, Alerta

class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = '__all__'

class AlertaSerializer(serializers.ModelSerializer):
    producto_str = serializers.SerializerMethodField()
    
    class Meta:
        model = Alerta
        fields = ['id', 'producto', 'producto_str', 'acueducto', 'umbral_minimo', 'activo']
        read_only_fields = ['id', 'producto_str']

    def get_producto_str(self, obj):
        return str(obj.producto) if obj.producto else "N/A"
