from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
from core.models import SoftDeleteModel, TimeStampedModel
from geography.models import Ubicacion

class Stock(TimeStampedModel):
    """Modelo unificado de stock."""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    producto = GenericForeignKey('content_type', 'object_id')
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, related_name='stocks_modular')
    cantidad = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal('0.000'))
    lote = models.CharField(max_length=50, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    estado_operativo = models.CharField(max_length=20, default='OPERATIVO')

    class Meta:
        db_table = 'inventario_stock'
        verbose_name = 'Existencia'
        unique_together = ('content_type', 'object_id', 'ubicacion', 'lote')

    def __str__(self):
        return f"{self.producto} @ {self.ubicacion}: {self.cantidad}"

class MovimientoInventario(SoftDeleteModel):
    """Registro de movimientos de inventario."""
    class TipoMovimiento(models.TextChoices):
        ENTRADA = 'ENTRADA', 'Entrada'
        SALIDA = 'SALIDA', 'Salida'
        TRANSFER = 'TRANSFER', 'Transferencia'
        AJUSTE = 'AJUSTE', 'Ajuste'
    
    class StatusMovimiento(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        APROBADO = 'APROBADO', 'Aprobado'
        RECHAZADO = 'RECHAZADO', 'Rechazado'

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    producto = GenericForeignKey('content_type', 'object_id')
    
    ubicacion_origen = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True, related_name='salidas_modular')
    ubicacion_destino = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True, related_name='entradas_modular')
    
    tipo_movimiento = models.CharField(max_length=20, choices=TipoMovimiento.choices)
    status = models.CharField(max_length=20, choices=StatusMovimiento.choices, default=StatusMovimiento.PENDIENTE)
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    razon = models.TextField(blank=True)
    
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='movimientos_creados_modular')
    aprobado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='movimientos_aprobados_modular')

    class Meta:
        db_table = 'inventario_movimientoinventario'
        verbose_name = 'Movimiento'
        ordering = ['-fecha_movimiento']

class InventoryAudit(models.Model):
    """Log de auditoría para movimientos."""
    class StatusAudit(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        SUCCESS = 'SUCCESS', 'Exitoso'
        FAILED = 'FAILED', 'Fallido'

    movimiento = models.ForeignKey(MovimientoInventario, on_delete=models.SET_NULL, null=True, related_name='audits_modular')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    producto = GenericForeignKey('content_type', 'object_id')
    
    tipo_movimiento = models.CharField(max_length=20, blank=True)
    cantidad = models.DecimalField(max_digits=12, decimal_places=3, null=True)
    
    ubicacion_origen = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    ubicacion_destino = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    
    status = models.CharField(max_length=20, choices=StatusAudit.choices, default=StatusAudit.PENDING)
    mensaje = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'inventario_inventoryaudit'
        verbose_name = 'Auditoría'
