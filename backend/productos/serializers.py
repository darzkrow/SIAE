from rest_framework import serializers
from core.serializers import BaseModelSerializer
from catalogo.serializers import CategoriaProductoSerializer
from productos.models import (
    UnitOfMeasure, ChemicalProduct, 
    Pipe, PumpAndMotor, Accessory
)
from proveedores.models import Supplier

class UnitOfMeasureSerializer(BaseModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    class Meta(BaseModelSerializer.Meta):
        model = UnitOfMeasure
        fields = BaseModelSerializer.Meta.fields + ['nombre', 'simbolo', 'tipo', 'tipo_display', 'activo']

# SupplierSerializer moved to proveedores app

class ProductListSerializer(BaseModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    unidad_medida_simbolo = serializers.CharField(source='unidad_medida.simbolo', read_only=True)
    proveedor_nombre = serializers.CharField(source='proveedor.nombre', read_only=True)
    
    class Meta(BaseModelSerializer.Meta):
        fields = BaseModelSerializer.Meta.fields + [
            'sku', 'nombre', 'categoria_nombre', 'unidad_medida_simbolo',
            'stock_actual', 'stock_minimo', 'precio_unitario', 'proveedor_nombre', 'activo'
        ]

class ChemicalProductSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = ChemicalProduct
        fields = '__all__'

class ChemicalProductListSerializer(ProductListSerializer):
    class Meta(ProductListSerializer.Meta):
        model = ChemicalProduct
        fields = ProductListSerializer.Meta.fields + ['es_peligroso', 'fecha_caducidad']

class PipeSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Pipe
        fields = '__all__'

class PipeListSerializer(ProductListSerializer):
    class Meta(ProductListSerializer.Meta):
        model = Pipe
        fields = ProductListSerializer.Meta.fields + ['material', 'diametro_nominal', 'presion_nominal']

class PumpAndMotorSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = PumpAndMotor
        fields = '__all__'

class PumpAndMotorListSerializer(ProductListSerializer):
    class Meta(ProductListSerializer.Meta):
        model = PumpAndMotor
        fields = ProductListSerializer.Meta.fields + ['tipo_equipo', 'modelo', 'potencia_hp']

class AccessorySerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Accessory
        fields = '__all__'

class AccessoryListSerializer(ProductListSerializer):
    class Meta(ProductListSerializer.Meta):
        model = Accessory
        fields = ProductListSerializer.Meta.fields + ['tipo_accesorio', 'material']
