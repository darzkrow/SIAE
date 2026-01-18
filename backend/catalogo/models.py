from django.db import models

class CategoriaProducto(models.Model):
    """Categorías generales de productos (Químicos, Tuberías, etc.)"""
    nombre = models.CharField(max_length=150, unique=True)
    codigo = models.CharField(
        max_length=10, 
        unique=True, 
        help_text='Código para generar SKU (ej: QUI, TUB, BOM)'
    )
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Categoría de Producto'
        verbose_name_plural = 'Categorías de Productos'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre

class Marca(models.Model):
    """Marcas de fabricantes de equipos y productos."""
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
