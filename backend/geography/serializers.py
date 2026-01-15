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
