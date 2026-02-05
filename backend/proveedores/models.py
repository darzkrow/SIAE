from django.db import models
from core.models import SoftDeleteModel

class Supplier(SoftDeleteModel):
    """🏢 Proveedores de productos y servicios"""
    nombre = models.CharField(max_length=200, unique=True)
    rif = models.CharField(max_length=30, blank=True, verbose_name='RIF')
    codigo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    contacto_nombre = models.CharField(max_length=150, blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'inventario_supplier'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']
        indexes = [models.Index(fields=['activo'])]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.codigo:
            last_s = Supplier.objects.order_by('-id').first()
            new_id = (last_s.id + 1) if last_s else 1
            self.codigo = f"PROV-{new_id:04d}"
        super().save(*args, **kwargs)
