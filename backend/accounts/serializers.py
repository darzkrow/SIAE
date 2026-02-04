from rest_framework import serializers
from core.serializers import BaseModelSerializer
from .models import CustomUser


class CustomUserSerializer(BaseModelSerializer):
    """Serializer para CustomUser heredando de BaseModelSerializer"""
    class Meta(BaseModelSerializer.Meta):
        model = CustomUser
        fields = BaseModelSerializer.Meta.fields + ['username', 'email', 'role', 'sucursal']
        read_only_fields = BaseModelSerializer.Meta.read_only_fields
