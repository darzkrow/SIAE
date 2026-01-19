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
    parish_nombre = serializers.SerializerMethodField()
    acueducto_nombre = serializers.SerializerMethodField()

    class Meta:
        from .models import Ubicacion
        model = Ubicacion
        fields = [
            'id', 'nombre', 'tipo', 'parish', 'parish_nombre',
            'acueducto', 'acueducto_nombre', 'descripcion', 'activa'
        ]

    def get_parish_nombre(self, obj):
        return obj.parish.name if obj.parish else None

    def get_acueducto_nombre(self, obj):
        return obj.acueducto.nombre if obj.acueducto else None
