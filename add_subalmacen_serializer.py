"""
Script para agregar Subalmacen serializer al archivo serializers.py
"""

# Leer el archivo serializers.py
with open(r'c:\Users\gfranco\Desktop\SIAE\backend\institucion\serializers.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Agregar import de Subalmacen
if "Subalmacen" not in content:
    content = content.replace(
        "from .models import (",
        "from .models import (\n    Subalmacen,"
    )

# Serializer de Subalmacen
subalmacen_serializer = '''

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
    
    class Meta(BaseModelSerializer.Meta):
        model = Subalmacen
        fields = BaseModelSerializer.Meta.fields + [
            'nombre', 'codigo', 'sucursal', 'sucursal_nombre',
            'estado', 'estado_nombre',
            'municipio', 'municipio_nombre',
            'parroquia', 'parroquia_nombre',
            'direccion', 'coordenadas_gps',
            'responsable', 'responsable_nombre',
            'capacidad', 'activo', 'descripcion',
            'ubicacion_completa',
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ['created_at', 'updated_at']
    
    def get_responsable_nombre(self, obj):
        if obj.responsable:
            return obj.responsable.get_full_name() or obj.responsable.username
        return None

'''

# Agregar antes de la sección de LEGACY SERIALIZERS
if "class SubalmacenSerializer" not in content:
    content = content.replace(
        "# ============================================================================\n# LEGACY SERIALIZERS",
        subalmacen_serializer + "\n# ============================================================================\n# LEGACY SERIALIZERS"
    )

# Guardar el archivo modificado
with open(r'c:\Users\gfranco\Desktop\SIAE\backend\institucion\serializers.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Subalmacen import agregado")
print("✅ SubalmacenSerializer agregado")
