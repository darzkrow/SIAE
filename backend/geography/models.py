from django.db import models
from institucion.models import Acueducto



class State(models.Model):
    name = models.CharField(max_length=128)
    
    class Meta:
        verbose_name = 'Estados'
        verbose_name_plural = 'Estados'

    def __str__(self):
        return self.name


class Municipality(models.Model):
    state = models.ForeignKey(State, related_name='municipalities', on_delete=models.CASCADE)
    name = models.CharField(max_length=128)

    class Meta:
        verbose_name = 'Municipio'
        verbose_name_plural = 'Municipios'

    def __str__(self):
        return f"{self.name} ({self.state})"


class Parish(models.Model):
    municipality = models.ForeignKey(Municipality, related_name='parishes', on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    class Meta:
        verbose_name = 'Parroquia'
        verbose_name_plural = 'Parroquias'

    def __str__(self):
        return f"{self.name} ({self.municipality})"


class Ubicacion(models.Model):
    """Ubicación física de un ítem, puede ser un almacén o una instalación."""
    
    class TipoUbicacion(models.TextChoices):
        ALMACEN = 'ALMACEN', 'Almacén'
        INSTALACION = 'INSTALACION', 'Instalación (Pozo, Estación, etc.)'

    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TipoUbicacion.choices)
    parish = models.ForeignKey(
        Parish,
        on_delete=models.PROTECT,
        related_name='ubicaciones',
        null=True, blank=True
    )
    acueducto = models.ForeignKey(
        Acueducto,
        on_delete=models.CASCADE,
        related_name='ubicaciones',
        null=True, blank=True
    )
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'
        unique_together = ('nombre', 'parish', 'acueducto')
        ordering = ['parish', 'acueducto', 'nombre']

    def __str__(self):
        if self.acueducto:
            return f"{self.nombre} ({self.acueducto.nombre})"
        if self.parish:
            return f"{self.nombre} ({self.parish.name})"
        return self.nombre
