from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimeStampedModel
from geography.models import State, Municipality, Parish

User = get_user_model()


class Subalmacen(TimeStampedModel):
    """
    Subalmacén (anteriormente Acueducto).
    Representa un punto de almacenamiento con ubicación geográfica específica.
    
    Este modelo reemplaza a Acueducto y agrega capacidad de ubicación geográfica
    precisa mediante relaciones con State, Municipality y Parish.
    """
    # Identificación
    nombre = models.CharField(
        max_length=200,
        help_text='Nombre del subalmacén'
    )
    codigo = models.CharField(
        max_length=20,
        unique=True,
        help_text='Código único del subalmacén (ej: SUB-ZUL-001)'
    )
    
    # Relación organizacional
    sucursal = models.ForeignKey(
        'Sucursal',
        on_delete=models.CASCADE,
        related_name='subalmacenes',
        help_text='Sucursal a la que pertenece este subalmacén'
    )
    
    # 🆕 Ubicación geográfica
    estado = models.ForeignKey(
        State,
        on_delete=models.PROTECT,
        related_name='subalmacenes',
        help_text='Estado donde se ubica el subalmacén'
    )
    municipio = models.ForeignKey(
        Municipality,
        on_delete=models.PROTECT,
        related_name='subalmacenes',
        null=True,
        blank=True,
        help_text='Municipio donde se ubica el subalmacén'
    )
    parroquia = models.ForeignKey(
        Parish,
        on_delete=models.PROTECT,
        related_name='subalmacenes',
        null=True,
        blank=True,
        help_text='Parroquia donde se ubica el subalmacén'
    )
    
    # Dirección detallada
    direccion = models.TextField(
        blank=True,
        help_text='Dirección completa del subalmacén'
    )
    coordenadas_gps = models.CharField(
        max_length=100,
        blank=True,
        help_text='Coordenadas GPS en formato "lat,lng" (ej: "10.123456,-66.654321")'
    )
    
    # Información adicional
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subalmacenes_responsable',
        help_text='Usuario responsable del subalmacén'
    )
    capacidad = models.IntegerField(
        null=True,
        blank=True,
        help_text='Capacidad de almacenamiento (unidades)'
    )
    activo = models.BooleanField(
        default=True,
        help_text='Indica si el subalmacén está activo'
    )
    
    # Descripción adicional
    descripcion = models.TextField(
        blank=True,
        help_text='Descripción adicional del subalmacén'
    )
    
    class Meta:
        verbose_name = 'Subalmacén'
        verbose_name_plural = 'Subalmacenes'
        unique_together = ('nombre', 'sucursal')
        ordering = ['estado__name', 'sucursal__nombre', 'nombre']
        indexes = [
            models.Index(fields=['estado', 'activo']),
            models.Index(fields=['sucursal', 'activo']),
            models.Index(fields=['codigo']),
            models.Index(fields=['estado', 'municipio']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({self.estado.name})"
    
    def get_ubicacion_completa(self):
        """Retorna ubicación geográfica completa como string"""
        partes = [self.estado.name]
        if self.municipio:
            partes.append(self.municipio.name)
        if self.parroquia:
            partes.append(self.parroquia.name)
        return ", ".join(partes)
    
    def es_responsable(self, user):
        """Verifica si un usuario es responsable de este subalmacén"""
        return self.responsable == user or user.is_staff
    
    def get_coordenadas_dict(self):
        """Retorna coordenadas GPS como diccionario"""
        if self.coordenadas_gps:
            try:
                lat, lng = self.coordenadas_gps.split(',')
                return {
                    'lat': float(lat.strip()),
                    'lng': float(lng.strip())
                }
            except (ValueError, AttributeError):
                return None
        return None
