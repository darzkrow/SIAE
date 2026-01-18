from rest_framework import viewsets, permissions, filters
from .models import AuditLog
from rest_framework import serializers

class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = AuditLog
        fields = '__all__'

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
