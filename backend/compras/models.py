from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from core.models import SoftDeleteModel, TimeStampedModel


class Correlativo(TimeStampedModel):
    """
    🔢 Manejo de numeración secuencial    
    Genera códigos únicos para órdenes de compra.
    Hereda timestamps de TimeStampedModel.
    """
    tipo = models.CharField(max_length=50, unique=True, help_text="Ej: ORDEN_COMPRA")
    prefijo = models.CharField(max_length=10)
    ultimo_numero = models.PositiveIntegerField(default=0)
    anio = models.PositiveIntegerField(default=timezone.now().year)

    def siguiente(self):
        self.ultimo_numero += 1
        self.save()
        return f"{self.prefijo}-{self.anio}-{self.ultimo_numero:05d}"

    class Meta:
        verbose_name = 'Correlativo'
        verbose_name_plural = 'Correlativos'


class OrdenCompra(SoftDeleteModel):
    """
    📋 Orden de compra
    
    Orden para adquisición de stock.
    Hereda timestamps y soft delete de SoftDeleteModel.
    """
    class Tipo(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', 'Individual'
        GLOBAL = 'GLOBAL', 'Global'

    class Status(models.TextChoices):
        BORRADOR = 'BORRADOR', 'Borrador'
        PENDIENTE_COMERCIALIZACION = 'PENDIENTE_COMERCIALIZACION', 'Pendiente Comercialización'
        PENDIENTE_PRESUPUESTO = 'PENDIENTE_PRESUPUESTO', 'Pendiente Presupuesto'
        PENDIENTE_FINANZAS = 'PENDIENTE_FINANZAS', 'Pendiente Finanzas'
        PENDIENTE_COMPRAS = 'PENDIENTE_COMPRAS', 'Pendiente Compras'
        EN_PROCESO = 'EN_PROCESO', 'En Proceso'
        COMPLETADO = 'COMPLETADO', 'Completado'
        CANCELADO = 'CANCELADO', 'Cancelado'

    codigo = models.CharField(max_length=50, unique=True, blank=True)
    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.INDIVIDUAL
    )
    
    # Jerarquía
    parent_order = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_orders',
        help_text='Orden Global a la que pertenece esta orden individual'
    )

    # Relación con movimiento (Solo para individuales)
    movimiento = models.OneToOneField(
        'stock.MovimientoInventario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orden_compra_v2' 
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # Solicitante original
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='ordenes_compra_solicitadas'
    )

    # Workflow de Aprobación
    # 1. Comercialización
    aprobado_comercializacion_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='ordenes_aprobadas_comercializacion'
    )
    fecha_aprobacion_comercializacion = models.DateTimeField(null=True, blank=True)
    
    # 2. Presupuesto
    aprobado_presupuesto_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='ordenes_aprobadas_presupuesto'
    )
    fecha_aprobacion_presupuesto = models.DateTimeField(null=True, blank=True)

    # 3. Finanzas
    aprobado_finanzas_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='ordenes_aprobadas_finanzas'
    )
    fecha_aprobacion_finanzas = models.DateTimeField(null=True, blank=True)

    # 4. Compras (Ejecución)
    ejecutado_compras_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='ordenes_ejecutadas_compras'
    )
    fecha_ejecucion_compras = models.DateTimeField(null=True, blank=True)

    # Estado
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.BORRADOR
    )
    
    notas = models.TextField(blank=True)
    motivo_cancelacion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Orden de Compra'
        verbose_name_plural = 'Órdenes de Compra'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.codigo

    def save(self, *args, **kwargs):
        if not self.codigo:
            correlativo, _ = Correlativo.objects.get_or_create(
                tipo='ORDEN_COMPRA',
                defaults={'prefijo': 'OC-G' if self.tipo == self.Tipo.GLOBAL else 'OC', 'anio': timezone.now().year}
            )
            self.codigo = correlativo.siguiente()
        super().save(*args, **kwargs)


class ItemOrden(SoftDeleteModel):
    """
    📦 Detalle de orden de compra
    
    Items individuales en una orden de compra.
    Hereda timestamps y soft delete de SoftDeleteModel.
    """
    orden = models.ForeignKey(
        OrdenCompra,
        on_delete=models.CASCADE,
        related_name='items'
    )
    # Relación Genérica al Producto
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    producto = GenericForeignKey('content_type', 'object_id')
    
    cantidad_pedida = models.DecimalField(max_digits=12, decimal_places=3)
    cantidad_recibida = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    precio_estimado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'Item de Orden'
        verbose_name_plural = 'Items de Órdenes'
