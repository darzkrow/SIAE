from rest_framework import serializers
from .models import State, Municipality, Parish


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name']


class MunicipalitySerializer(serializers.ModelSerializer):
    state = StateSerializer(read_only=True)

    class Meta:
        model = Municipality
        fields = ['id', 'name', 'state']


class ParishSerializer(serializers.ModelSerializer):
    municipality = MunicipalitySerializer(read_only=True)

    class Meta:
        model = Parish
        fields = ['id', 'name', 'municipality']


class UbicacionSerializer(serializers.ModelSerializer):
    parish_nombre = serializers.CharField(source='parish.name', read_only=True)
    acueducto_nombre = serializers.CharField(source='acueducto.nombre', read_only=True)

    class Meta:
        from .models import Ubicacion
        model = Ubicacion
        fields = [
            'id', 'nombre', 'tipo', 'parish', 'parish_nombre',
            'acueducto', 'acueducto_nombre', 'descripcion', 'activa'
        ]
