from django.db import models
from core.models import SoftDeleteModel, TimeStampedModel


class CategoriaProducto(SoftDeleteModel):
    """
    📦 Categorías generales de productos
    
    Categorías principales como Químicos, Tuberías, Bombas, etc.
    Hereda timestamps y soft delete de SoftDeleteModel.
    """
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


class Marca(SoftDeleteModel):
    """
    🏷️ Marcas de fabricantes
    
    Marcas de equipos y productos.
    Hereda timestamps y soft delete de SoftDeleteModel.
    """
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Tag(TimeStampedModel):
    """
    🏷️ Tags para clasificación flexible de productos
    
    Permite etiquetar productos con múltiples categorías
    para búsqueda y filtrado avanzado.
    Hereda timestamps de TimeStampedModel.
    """
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(
        max_length=7, 
        default='#007bff', 
        help_text='Hex color code for the tag'
    )
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']

    def __str__(self):
        return self.name
