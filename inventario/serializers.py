"""
Serializers para el sistema de inventario refactorizado.
Usar con los modelos de models_refactored_consolidated.py
"""
from rest_framework import serializers
from decimal import Decimal

from inventario.models import (
    OrganizacionCentral, Sucursal, Acueducto,
    Category, UnitOfMeasure, Supplier,
    ChemicalProduct, Pipe, PumpAndMotor, Accessory,
    StockChemical, StockPipe, StockPumpAndMotor, StockAccessory
)


# ============================================================================
# SERIALIZERS DE MODELOS AUXILIARES
# ============================================================================

class CategorySerializer(serializers.ModelSerializer):
    """Serializer para categorías de productos."""
    total_productos = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'nombre', 'codigo', 'descripcion',
            'activo', 'orden', 'total_productos'
        ]
        read_only_fields = ['id']
    
    def get_total_productos(self, obj):
        """Cuenta total de productos en esta categoría."""
        # Implementar después de la migración
        return 0


class UnitOfMeasureSerializer(serializers.ModelSerializer):
    """Serializer para unidades de medida."""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = UnitOfMeasure
        fields = ['id', 'nombre', 'simbolo', 'tipo', 'tipo_display', 'activo']
        read_only_fields = ['id']


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer para proveedores."""
    total_productos = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'nombre', 'rif', 'codigo', 'contacto_nombre',
            'telefono', 'email', 'direccion', 'activo',
            'creado_en', 'actualizado_en', 'total_productos'
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']
    
    def get_total_productos(self, obj):
        """Total de productos de este proveedor."""
        return 0  # Implementar después


class AcueductoSerializer(serializers.ModelSerializer):
    """Serializer para acueductos."""
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    
    class Meta:
        from inventario.models import Acueducto
        model = Acueducto
        fields = ['id', 'nombre', 'sucursal', 'sucursal_nombre', 'ubicacion']
        read_only_fields = ['id']


# ============================================================================
# SERIALIZERS BASE PARA PRODUCTOS
# ============================================================================

class ProductBaseSerializer(serializers.ModelSerializer):
    """Serializer base para todos los productos."""
    # Nested serializers para lectura
    categoria_detail = CategorySerializer(source='categoria', read_only=True)
    unidad_medida_detail = UnitOfMeasureSerializer(source='unidad_medida', read_only=True)
    proveedor_detail = SupplierSerializer(source='proveedor', read_only=True)
    
    # Display fields
    stock_status = serializers.CharField(source='get_stock_status', read_only=True)
    stock_percentage = serializers.SerializerMethodField()
    valor_total = serializers.SerializerMethodField()
    
    # Writable nested fields (IDs)
    categoria = serializers.PrimaryKeyRelatedField(queryset='Category.objects.all()')
    unidad_medida = serializers.PrimaryKeyRelatedField(queryset='UnitOfMeasure.objects.all()')
    proveedor = serializers.PrimaryKeyRelatedField(queryset='Supplier.objects.all()')
    
    def get_stock_percentage(self, obj):
        """Porcentaje de stock vs mínimo."""
        return obj.get_stock_percentage()
    
    def get_valor_total(self, obj):
        """Valor total del stock."""
        return float(obj.stock_actual * obj.precio_unitario)


# ============================================================================
# SERIALIZERS DE PRODUCTOS ESPECÍFICOS
# ============================================================================

class ChemicalProductSerializer(ProductBaseSerializer):
    """Serializer para productos químicos."""
    nivel_peligrosidad_display = serializers.CharField(
        source='get_nivel_peligrosidad_display', 
        read_only=True
    )
    presentacion_display = serializers.CharField(
        source='get_presentacion_display', 
        read_only=True
    )
    unidad_concentracion_display = serializers.CharField(
        source='get_unidad_concentracion_display', 
        read_only=True
    )
    is_expired = serializers.BooleanField(source='is_expired', read_only=True)
    days_until_expiration = serializers.IntegerField(
        source='days_until_expiration', 
        read_only=True
    )
    
    class Meta:
        model = ChemicalProduct
        fields = [
            # Campos base
            'id', 'sku', 'nombre', 'descripcion',
            'categoria', 'categoria_detail',
            'unidad_medida', 'unidad_medida_detail',
            'stock_actual', 'stock_minimo', 'precio_unitario',
            'proveedor', 'proveedor_detail',
            'activo', 'fecha_entrada', 'notas',
            'creado_en', 'actualizado_en',
            
            # Campos específicos de químicos
            'es_peligroso', 'nivel_peligrosidad', 'nivel_peligrosidad_display',
            'fecha_caducidad', 'concentracion', 'unidad_concentracion',
            'unidad_concentracion_display', 'presentacion', 'presentacion_display',
            'peso_neto', 'ficha_seguridad', 'numero_un',
            
            # Campos calculados
            'stock_status', 'stock_percentage', 'valor_total',
            'is_expired', 'days_until_expiration'
        ]
        read_only_fields = [
            'id', 'sku', 'creado_en', 'actualizado_en',
            'stock_status', 'stock_percentage', 'valor_total'
        ]
    
    def validate(self, data):
        """Validaciones personalizadas."""
        if data.get('es_peligroso') and not data.get('nivel_peligrosidad'):
            raise serializers.ValidationError({
                'nivel_peligrosidad': 'Requerido para productos peligrosos'
            })
        return data


class PipeSerializer(ProductBaseSerializer):
    """Serializer para tuberías."""
    material_display = serializers.CharField(source='get_material_display', read_only=True)
    unidad_diametro_display = serializers.CharField(source='get_unidad_diametro_display', read_only=True)
    presion_nominal_display = serializers.CharField(source='get_presion_nominal_display', read_only=True)
    tipo_union_display = serializers.CharField(source='get_tipo_union_display', read_only=True)
    tipo_uso_display = serializers.CharField(source='get_tipo_uso_display', read_only=True)
    diametro_display = serializers.CharField(source='get_diametro_display', read_only=True)
    
    class Meta:
        model = 'Pipe'
        fields = [
            # Campos base
            'id', 'sku', 'nombre', 'descripcion',
            'categoria', 'categoria_detail',
            'unidad_medida', 'unidad_medida_detail',
            'stock_actual', 'stock_minimo', 'precio_unitario',
            'proveedor', 'proveedor_detail',
            'activo', 'fecha_entrada', 'notas',
            'creado_en', 'actualizado_en',
            
            # Campos específicos de tuberías
            'material', 'material_display',
            'diametro_nominal', 'unidad_diametro', 'unidad_diametro_display',
            'diametro_display', 'presion_nominal', 'presion_nominal_display',
            'presion_psi', 'longitud_unitaria', 'tipo_union', 'tipo_union_display',
            'tipo_uso', 'tipo_uso_display', 'espesor_pared',
            
            # Campos calculados
            'stock_status', 'stock_percentage', 'valor_total',
        ]
        read_only_fields = [
            'id', 'sku', 'presion_psi', 'creado_en', 'actualizado_en',
            'stock_status', 'stock_percentage', 'valor_total'
        ]


class PumpAndMotorSerializer(ProductBaseSerializer):
    """Serializer para bombas y motores."""
    tipo_equipo_display = serializers.CharField(source='get_tipo_equipo_display', read_only=True)
    fases_display = serializers.CharField(source='get_fases_display', read_only=True)
    potencia_display = serializers.CharField(source='get_potencia_display', read_only=True)
    
    class Meta:
        model = 'PumpAndMotor'
        fields = [
            # Campos base
            'id', 'sku', 'nombre', 'descripcion',
            'categoria', 'categoria_detail',
            'unidad_medida', 'unidad_medida_detail',
            'stock_actual', 'stock_minimo', 'precio_unitario',
            'proveedor', 'proveedor_detail',
            'activo', 'fecha_entrada', 'notas',
            'creado_en', 'actualizado_en',
            
            # Identificación
            'tipo_equipo', 'tipo_equipo_display',
            'marca', 'modelo', 'numero_serie',
            
            # Eléctricos
            'potencia_hp', 'potencia_kw', 'potencia_display',
            'voltaje', 'fases', 'fases_display', 'frecuencia', 'amperaje',
            
            # Hidráulicos
            'caudal_maximo', 'unidad_caudal', 'altura_dinamica',
            'eficiencia', 'npsh_requerido', 'curva_caracteristica',
            
            # Campos calculados
            'stock_status', 'stock_percentage', 'valor_total',
        ]
        read_only_fields = [
            'id', 'sku', 'potencia_kw', 'creado_en', 'actualizado_en',
            'stock_status', 'stock_percentage', 'valor_total'
        ]


class AccessorySerializer(ProductBaseSerializer):
    """Serializer para accesorios."""
    tipo_accesorio_display = serializers.CharField(source='get_tipo_accesorio_display', read_only=True)
    tipo_conexion_display = serializers.CharField(source='get_tipo_conexion_display', read_only=True)
    material_display = serializers.CharField(source='get_material_display', read_only=True)
    dimension_display = serializers.CharField(source='get_dimension_display', read_only=True)
    
    class Meta:
        model = 'Accessory'
        fields = [
            # Campos base
            'id', 'sku', 'nombre', 'descripcion',
            'categoria', 'categoria_detail',
            'unidad_medida', 'unidad_medida_detail',
            'stock_actual', 'stock_minimo', 'precio_unitario',
            'proveedor', 'proveedor_detail',
            'activo', 'fecha_entrada', 'notas',
            'creado_en', 'actualizado_en',
            
            # Específicos
            'tipo_accesorio', 'tipo_accesorio_display', 'subtipo',
            'diametro_entrada', 'diametro_salida', 'unidad_diametro',
            'dimension_display', 'tipo_conexion', 'tipo_conexion_display',
            'angulo', 'presion_trabajo', 'material', 'material_display',
            
            # Campos calculados
            'stock_status', 'stock_percentage', 'valor_total',
        ]
        read_only_fields = [
            'id', 'sku', 'creado_en', 'actualizado_en',
            'stock_status', 'stock_percentage', 'valor_total'
        ]


# ============================================================================
# SERIALIZERS DE STOCK
# ============================================================================

class StockChemicalSerializer(serializers.ModelSerializer):
    """Serializer para stock de químicos."""
    producto_detail = ChemicalProductSerializer(source='producto', read_only=True)
    acueducto_detail = serializers.StringRelatedField(source='acueducto', read_only=True)
    
    class Meta:
        model = StockChemical
        fields = [
            'id', 'producto', 'producto_detail',
            'acueducto', 'acueducto_detail',
            'cantidad', 'lote', 'fecha_vencimiento',
            'ubicacion_fisica', 'fecha_ultima_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_ultima_actualizacion']


class StockPipeSerializer(serializers.ModelSerializer):
    """Serializer para stock de tuberías."""
    producto_detail = PipeSerializer(source='producto', read_only=True)
    acueducto_detail = serializers.StringRelatedField(source='acueducto', read_only=True)
    
    class Meta:
        model = StockPipe
        fields = [
            'id', 'producto', 'producto_detail',
            'acueducto', 'acueducto_detail',
            'cantidad', 'metros_totales', 'ubicacion_fisica',
            'fecha_ultima_actualizacion'
        ]
        read_only_fields = ['id', 'metros_totales', 'fecha_ultima_actualizacion']


class StockPumpAndMotorSerializer(serializers.ModelSerializer):
    """Serializer para stock de bombas/motores."""
    producto_detail = PumpAndMotorSerializer(source='producto', read_only=True)
    acueducto_detail = serializers.StringRelatedField(source='acueducto', read_only=True)
    estado_operativo_display = serializers.CharField(
        source='get_estado_operativo_display', 
        read_only=True
    )
    
    class Meta:
        model = StockPumpAndMotor
        fields = [
            'id', 'producto', 'producto_detail',
            'acueducto', 'acueducto_detail',
            'cantidad', 'estado_operativo', 'estado_operativo_display',
            'ubicacion_fisica', 'fecha_ultima_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_ultima_actualizacion']


class StockAccessorySerializer(serializers.ModelSerializer):
    """Serializer para stock de accesorios."""
    producto_detail = AccessorySerializer(source='producto', read_only=True)
    acueducto_detail = serializers.StringRelatedField(source='acueducto', read_only=True)
    
    class Meta:
        model = StockAccessory
        fields = [
            'id', 'producto', 'producto_detail',
            'acueducto', 'acueducto_detail',
            'cantidad', 'ubicacion_fisica',
            'fecha_ultima_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_ultima_actualizacion']



# ============================================================================
# SERIALIZERS DE MOVIMIENTOS
# ============================================================================

class MovimientoInventarioSerializer(serializers.ModelSerializer):
    """Serializer para movimientos de inventario con soporte genérico."""
    producto_str = serializers.SerializerMethodField()
    creado_por_username = serializers.SerializerMethodField()
    acueducto_origen_nombre = serializers.CharField(source='acueducto_origen.nombre', read_only=True, allow_null=True)
    acueducto_destino_nombre = serializers.CharField(source='acueducto_destino.nombre', read_only=True, allow_null=True)
    
    # Campos de lectura para la relación genérica
    product_type_read = serializers.SerializerMethodField()
    product_id_read = serializers.SerializerMethodField()
    
    # Campos para escritura
    product_type = serializers.CharField(write_only=True)  # 'chemical', 'pipe', 'pump', 'accessory'
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        from inventario.models import MovimientoInventario
        model = MovimientoInventario
        fields = [
            'id', 'tipo_movimiento', 'cantidad', 'fecha_movimiento',
            'acueducto_origen', 'acueducto_origen_nombre',
            'acueducto_destino', 'acueducto_destino_nombre',
            'producto_str', 'razon', 'creado_por_username',
            'product_type', 'product_id',
            'product_type_read', 'product_id_read'
        ]
        read_only_fields = ['id', 'fecha_movimiento', 'producto_str', 'creado_por_username']

    def get_creado_por_username(self, obj):
        if obj.creado_por:
            return obj.creado_por.username
        return None

    def get_producto_str(self, obj):
        if obj.producto:
            return str(obj.producto)
        return "Producto eliminado o no encontrado"

    def get_product_type_read(self, obj):
        if obj.content_type:
            return obj.content_type.model
        return None

    def get_product_id_read(self, obj):
        return obj.object_id

    def create(self, validated_data):
        product_type = validated_data.pop('product_type')

        product_id = validated_data.pop('product_id')
        
        # Mapear string a ContentType
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
        
        # Asignar usuario si está en el contexto
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['creado_por'] = request.user
            
        return super().create(validated_data)


# ============================================================================
# SERIALIZERS PARA LISTADOS SIMPLIFICADOS
# ============================================================================

class ChemicalProductListSerializer(serializers.ModelSerializer):
    """Serializer simple para listados de químicos."""
    stock_status = serializers.CharField(source='get_stock_status', read_only=True)
    
    class Meta:
        model = ChemicalProduct
        fields = [
            'id', 'sku', 'nombre', 'stock_actual', 'stock_minimo',
            'stock_status', 'es_peligroso', 'fecha_caducidad', 'presentacion'
        ]


class PipeListSerializer(serializers.ModelSerializer):
    """Serializer simple para listados de tuberías."""
    stock_status = serializers.CharField(source='get_stock_status', read_only=True)
    
    class Meta:
        model = 'Pipe'
        fields = [
            'id', 'sku', 'nombre', 'material', 'diametro_nominal',
            'stock_actual', 'stock_minimo', 'stock_status'
        ]


class PumpAndMotorListSerializer(serializers.ModelSerializer):
    """Serializer simple para listados de bombas."""
    stock_status = serializers.CharField(source='get_stock_status', read_only=True)
    
    class Meta:
        model = 'PumpAndMotor'
        fields = [
            'id', 'sku', 'nombre', 'tipo_equipo', 'marca', 'modelo',
            'potencia_hp', 'stock_actual', 'stock_minimo', 'stock_status'
        ]


class AccessoryListSerializer(serializers.ModelSerializer):
    """Serializer simple para listados de accesorios."""
    stock_status = serializers.CharField(source='get_stock_status', read_only=True)
    
    class Meta:
        model = 'Accessory'
        fields = [
            'id', 'sku', 'nombre', 'tipo_accesorio', 'tipo_conexion',
            'stock_actual', 'stock_minimo', 'stock_status'
        ]


# ============================================================================
# SERIALIZERS DE ALERTAS Y NOTIFICACIONES
# ============================================================================


class AlertaSerializer(serializers.ModelSerializer):
    """Serializer para alertas de stock."""
    producto_str = serializers.SerializerMethodField()
    acueducto_nombre = serializers.CharField(source='acueducto.nombre', read_only=True)
    
    # Campos para escritura GFK
    product_type = serializers.CharField(write_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        from inventario.models import Alerta
        model = Alerta
        fields = [
            'id', 'acueducto', 'acueducto_nombre', 
            'umbral_minimo', 'activo', 'producto_str',
            'product_type', 'product_id'
        ]
        read_only_fields = ['id', 'producto_str']

    def get_producto_str(self, obj):
        if obj.producto:
            return str(obj.producto)
        return "Producto no encontrado"

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
        model_name = type_map.get(product_type, product_type)
        try:
            ct = ContentType.objects.get(app_label='inventario', model=model_name)
        except ContentType.DoesNotExist:
             raise serializers.ValidationError({'product_type': 'Tipo inválido'})
             
        validated_data['content_type'] = ct
        validated_data['object_id'] = product_id
        return super().create(validated_data)


class NotificacionSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones."""
    class Meta:
        from inventario.models import Notificacion
        model = Notificacion
        fields = '__all__'
