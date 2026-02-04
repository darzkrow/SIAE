from rest_framework import serializers

class BaseModelSerializer(serializers.ModelSerializer):
    """
    🏗️ Serializer Base para Modelos
    
    Incluye campos comunes y validaciones estándar.
    """
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        abstract = True
        fields = ['id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SoftDeleteSerializer(BaseModelSerializer):
    """
    🗑️ Serializer para Modelos con Soft Delete
    
    Incluye el campo deleted_at.
    """
    deleted_at = serializers.DateTimeField(read_only=True)
    is_deleted = serializers.BooleanField(read_only=True)

    class Meta(BaseModelSerializer.Meta):
        fields = BaseModelSerializer.Meta.fields + ['deleted_at', 'is_deleted']
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ['deleted_at']
