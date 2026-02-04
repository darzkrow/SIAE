from rest_framework import viewsets, filters
from .models import Notificacion, Alerta
from .serializers import NotificacionSerializer, AlertaSerializer
from rest_framework.permissions import IsAuthenticated
from auditoria.mixins import AuditMixin, TrashBinMixin

class NotificacionViewSet(AuditMixin, TrashBinMixin, viewsets.ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['leida', 'tipo']
    
    def get_queryset(self):
        """Optimize queryset with select_related."""
        return super().get_queryset().select_related('user')

class AlertaViewSet(AuditMixin, TrashBinMixin, viewsets.ModelViewSet):
    queryset = Alerta.objects.all()
    serializer_class = AlertaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['activo', 'acueducto']
    
    def get_queryset(self):
        """Optimize queryset with select_related."""
        return super().get_queryset().select_related(
            'acueducto__sucursal'
        )
