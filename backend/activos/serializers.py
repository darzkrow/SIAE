from rest_framework import serializers
from core.serializers import BaseModelSerializer
from activos.models import MaterialEstrategico, ActivoFijo, FichaTecnicaMotor, RegistroMantenimiento

class MaterialEstrategicoSerializer(BaseModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    class Meta(BaseModelSerializer.Meta):
        model = MaterialEstrategico
        fields = '__all__'

class ActivoFijoSerializer(BaseModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    class Meta(BaseModelSerializer.Meta):
        model = ActivoFijo
        fields = '__all__'

class FichaTecnicaMotorSerializer(serializers.ModelSerializer):
    class Meta:
        model = FichaTecnicaMotor
        fields = '__all__'

class RegistroMantenimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroMantenimiento
        fields = '__all__'
