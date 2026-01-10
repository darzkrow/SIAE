from rest_framework import serializers
from accounts.models import CustomUser
from .models import (
    OrganizacionCentral, Sucursal, Acueducto, 
    Categoria, Tuberia, Equipo, StockTuberia, StockEquipo, 
    MovimientoInventario, InventoryAudit, AlertaStock, Notification
)

class OrganizacionCentralSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizacionCentral
        fields = '__all__'

class SucursalSerializer(serializers.ModelSerializer):
    organizacion_central_nombre = serializers.ReadOnlyField(source='organizacion_central.nombre')
    
    class Meta:
        model = Sucursal
        fields = '__all__'

class AcueductoSerializer(serializers.ModelSerializer):
    sucursal_nombre = serializers.ReadOnlyField(source='sucursal.nombre')
    
    class Meta:
        model = Acueducto
        fields = '__all__'

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class TuberiaSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')
    
    class Meta:
        model = Tuberia
        fields = '__all__'

class EquipoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')
    
    class Meta:
        model = Equipo
        fields = '__all__'

class StockTuberiaSerializer(serializers.ModelSerializer):
    tuberia_detalle = TuberiaSerializer(source='tuberia', read_only=True)
    acueducto_nombre = serializers.ReadOnlyField(source='acueducto.nombre')
    
    class Meta:
        model = StockTuberia
        fields = '__all__'

class StockEquipoSerializer(serializers.ModelSerializer):
    equipo_detalle = EquipoSerializer(source='equipo', read_only=True)
    acueducto_nombre = serializers.ReadOnlyField(source='acueducto.nombre')
    
    class Meta:
        model = StockEquipo
        fields = '__all__'

class MovimientoInventarioSerializer(serializers.ModelSerializer):
    articulo_nombre = serializers.ReadOnlyField(source='get_articulo_display_name')
    acueducto_origen_nombre = serializers.ReadOnlyField(source='acueducto_origen.nombre')
    acueducto_destino_nombre = serializers.ReadOnlyField(source='acueducto_destino.nombre')
    
    class Meta:
        model = MovimientoInventario
        fields = '__all__'

class InventoryAuditSerializer(serializers.ModelSerializer):
    movimiento_id = serializers.ReadOnlyField(source='movimiento.id')
    acueducto_origen_nombre = serializers.ReadOnlyField(source='acueducto_origen.nombre')
    acueducto_destino_nombre = serializers.ReadOnlyField(source='acueducto_destino.nombre')
    
    class Meta:
        model = InventoryAudit
        fields = '__all__'

class AlertaStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertaStock
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    sucursal_nombre = serializers.ReadOnlyField(source='sucursal.nombre')
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'sucursal', 'sucursal_nombre', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
