from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Correlativo(models.Model):
    """Manejo de numeración secuencial para órdenes."""
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

class OrdenCompra(models.Model):
    """Orden de compra para adquisición de stock."""
    class Status(models.TextChoices):
        BORRADOR = 'BORRADOR', 'Borrador'
        SOLICITADO = 'SOLICITADO', 'Solicitado'
        PROCESO = 'EN_PROCESO', 'En Proceso'
        COMPLETADO = 'COMPLETADO', 'Completado'
        CANCELADO = 'CANCELADO', 'Cancelado'

    codigo = models.CharField(max_length=50, unique=True)
    movimiento = models.OneToOneField(
        'inventario.MovimientoInventario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orden_compra_v2' # New relation name to avoid conflict during migration
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='ordenes_compra_solicitadas'
    )
    aprobador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='ordenes_compra_aprobadas'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.BORRADOR
    )
    notas = models.TextField(blank=True)

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
                defaults={'prefijo': 'OC', 'anio': timezone.now().year}
            )
            self.codigo = correlativo.siguiente()
        super().save(*args, **kwargs)

class ItemOrden(models.Model):
    """Detalle de productos en una orden de compra."""
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
