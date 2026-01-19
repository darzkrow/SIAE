from django.db import models

# ============================================================================
# MODELOS ORGANIZACIONALES (Mantener compatibilidad)
# ============================================================================

class OrganizacionCentral(models.Model):
    """Organización central que agrupa sucursales. Puede ser jerárquica (Ministerio -> Ente)."""
    nombre = models.CharField(max_length=200, unique=True)
    rif = models.CharField(max_length=30, blank=True, verbose_name='RIF')
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_organizaciones',
        help_text='Organización superior (ej: MINAGUAS)'
    )

    class Meta:
        verbose_name = 'Organización Central'
        verbose_name_plural = 'Organizaciones Centrales'
        ordering = ['nombre']

    def __str__(self):
        if self.parent:
            return f"{self.nombre} ← {self.parent.nombre}"
        return self.nombre


class Sucursal(models.Model):
    """Sucursal operativa de la organización."""
    nombre = models.CharField(max_length=200, unique=True)
    organizacion_central = models.ForeignKey(
        OrganizacionCentral,
        on_delete=models.PROTECT,
        related_name='sucursales'
    )
    codigo = models.CharField(max_length=10, unique=True, blank=True, null=True)
    direccion = models.TextField(blank=True)
    telefono = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.organizacion_central.nombre})"


class Acueducto(models.Model):
    """Acueducto o sistema de agua potable."""
    nombre = models.CharField(max_length=200)
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.CASCADE,
        related_name='acueductos'
    )
    codigo = models.CharField(max_length=10, blank=True)
    ubicacion = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Acueducto'
        verbose_name_plural = 'Acueductos'
        unique_together = ('nombre', 'sucursal')
        ordering = ['sucursal', 'nombre']

    def __str__(self):
        return f"{self.nombre} - {self.sucursal.nombre}"
