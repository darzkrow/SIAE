from rest_framework import viewsets, permissions, filters
from .models import AuditLog
from rest_framework import serializers

class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'action',
            'content_type', 'object_id',
            'object_repr', 'changes',
            'ip_address', 'user_agent', 'timestamp'
        ]

    def get_user_name(self, obj):
        return obj.user.username if obj.user else None

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para visualizar los logs de auditoría. Solo lectura.
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['object_repr', 'user__username', 'action']
    ordering_fields = ['timestamp']
