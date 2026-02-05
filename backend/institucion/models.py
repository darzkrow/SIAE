from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from mptt.models import MPTTModel, TreeForeignKey
from core.models import TimeStampedModel
from geography.models import State, Municipality, Parish
import qrcode
from io import BytesIO
from django.core.files import File
from django.urls import reverse
from .choices import VicepresidenciaTypes, TipoUnidadChoices, AlmacenPrefijos
User = get_user_model()

class Empresa(TimeStampedModel, MPTTModel):
    """
    🏢 Empresa en jerarquía organizacional
    
    Hereda created_at y updated_at de TimeStampedModel.
    """
    nombre = models.CharField(max_length=200, unique=True)
    codigo = models.CharField(max_length=10, unique=True)
    rif = models.CharField(max_length=30, blank=True, verbose_name='RIF')
    direccion = models.TextField(blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)

    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subsidiarias'
    )
    
    class MPTTMeta:
        order_insertion_by = ['nombre']
        
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
            models.Index(fields=['created_at']),  # Using inherited field
        ]
    
    def __str__(self):
        return self.nombre
    
    def get_full_path(self):
        """Return full hierarchical path"""
        ancestors = self.get_ancestors(include_self=True)
        return ' → '.join([ancestor.nombre for ancestor in ancestors])




class Vicepresidencia(TimeStampedModel, MPTTModel):
    """
    🏛️ Vicepresidencias (Comercialización, Operaciones Hídricas, Administrativa)
    
    Segundo nivel en jerarquía organizacional.
    Hereda created_at y updated_at de TimeStampedModel.
    """
    
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='vicepresidencias'
    )
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=50, choices=VicepresidenciaTypes.choices)
    descripcion = models.TextField(blank=True)
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vicepresidencias_responsable'
    )
    activo = models.BooleanField(default=True)
    # fecha_creacion y fecha_actualizacion heredados de TimeStampedModel
    
    # MPTT fields
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_vicepresidencias'
    )
    
    class MPTTMeta:
        order_insertion_by = ['nombre']
        
    class Meta:
        verbose_name = 'Vicepresidencia'
        verbose_name_plural = 'Vicepresidencias'
        ordering = ['empresa', 'tipo', 'nombre']
        unique_together = ['empresa', 'codigo']
        indexes = [
            models.Index(fields=['empresa', 'tipo']),
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
            models.Index(fields=['tipo']),
        ]
    
    def __str__(self):
        return f"{self.nombre} - {self.empresa.nombre}"
    
    def get_full_path(self):
        """Return full hierarchical path"""
        path = [self.empresa.nombre]
        ancestors = self.get_ancestors(include_self=True)
        path.extend([ancestor.nombre for ancestor in ancestors])
        return ' → '.join(path)


class UnidadOrganizacional(TimeStampedModel, MPTTModel):
    """
    🏛️ Unidades organizacionales genéricas
    
    Tercer nivel en jerarquía organizacional.
    Hereda created_at y updated_at de TimeStampedModel.
    """
    
    vicepresidencia = models.ForeignKey(
        Vicepresidencia,
        on_delete=models.CASCADE,
        related_name='unidades_organizacionales'
    )
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=30, unique=True)
    tipo = models.CharField(max_length=50, choices=TipoUnidadChoices.choices)
    descripcion = models.TextField(blank=True)
    ubicacion = models.CharField(max_length=255, blank=True)
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='unidades_responsable'
    )
    activo = models.BooleanField(default=True)
    # fecha_creacion y fecha_actualizacion heredados de TimeStampedModel
    
    # MPTT fields
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_unidades'
    )
    
    class MPTTMeta:
        order_insertion_by = ['nombre']
        
    class Meta:
        verbose_name = 'Unidad Organizacional'
        verbose_name_plural = 'Unidades Organizacionales'
        ordering = ['vicepresidencia', 'tipo', 'nombre']
        unique_together = ['vicepresidencia', 'codigo']
        indexes = [
            models.Index(fields=['vicepresidencia', 'tipo']),
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
            models.Index(fields=['tipo']),
            models.Index(fields=['ubicacion']),
        ]
    
    def __str__(self):
        return f"{self.nombre} - {self.vicepresidencia.nombre}"
    
    def get_full_path(self):
        """Return full hierarchical path"""
        path = [self.vicepresidencia.empresa.nombre, self.vicepresidencia.nombre]
        ancestors = self.get_ancestors(include_self=True)
        path.extend([ancestor.nombre for ancestor in ancestors])
        return ' → '.join(path)


class AlmacenRegional(TimeStampedModel):
    """
    🏬 9 almacenes regionales bajo VP Operaciones
    
    Cada almacén tiene un código único de tres letras.
    Hereda created_at y updated_at de TimeStampedModel.
    """
    
    unidad_organizacional = models.ForeignKey(
        UnidadOrganizacional,
        on_delete=models.CASCADE,
        related_name='almacenes_regionales',
        help_text='Unidad organizacional bajo VP Operaciones'
    )
    nombre = models.CharField(
        max_length=200,
        help_text='Nombre del almacén regional'
    )
    prefijo = models.CharField(
        max_length=3,
        unique=True,
        choices=AlmacenPrefijos.choices,
        help_text='Código único de tres letras para identificar el almacén'
    )
    ubicacion = models.CharField(
        max_length=200,
        help_text='Ubicación física del almacén'
    )
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='almacenes_gestionados',
        help_text='Gerente responsable del almacén'
    )
    capacidad_maxima = models.IntegerField(
        default=10000,
        validators=[MinValueValidator(1)],
        help_text='Capacidad máxima de almacenamiento'
    )
    activo = models.BooleanField(
        default=True,
        help_text='Indica si el almacén está activo'
    )
    # fecha_creacion y fecha_actualizacion heredados de TimeStampedModel
    
    # Additional fields for warehouse management
    descripcion = models.TextField(
        blank=True,
        help_text='Descripción adicional del almacén'
    )
    telefono = models.CharField(
        max_length=50,
        blank=True,
        help_text='Teléfono de contacto del almacén'
    )
    email = models.EmailField(
        blank=True,
        help_text='Email de contacto del almacén'
    )
    
    class Meta:
        verbose_name = 'Almacén Regional'
        verbose_name_plural = 'Almacenes Regionales'
        ordering = ['prefijo', 'nombre']
        indexes = [
            models.Index(fields=['prefijo']),
            models.Index(fields=['activo']),
            models.Index(fields=['unidad_organizacional']),
            models.Index(fields=['manager']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['prefijo'],
                name='unique_almacen_prefijo'
            ),
        ]
    
    def __str__(self):
        return f"{self.prefijo} - {self.nombre}"
    
    def clean(self):
        """Custom validation for AlmacenRegional"""
        from django.core.exceptions import ValidationError
        
        # Validate that the prefix is one of the predefined valid prefixes
        valid_prefixes = [prefix for prefix, _ in self.PREFIJOS_VALIDOS]
        if self.prefijo and self.prefijo not in valid_prefixes:
            raise ValidationError({
                'prefijo': f'El prefijo debe ser uno de los siguientes: {", ".join(valid_prefixes)}'
            })
        
        # Validate that the unidad_organizacional belongs to VP Operations
        if self.unidad_organizacional:
            vp = self.unidad_organizacional.vicepresidencia
            if vp.tipo != 'OPERACIONES_HIDRICAS':
                raise ValidationError({
                    'unidad_organizacional': 'El almacén regional debe pertenecer a una unidad bajo VP Operaciones Hídricas'
                })
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_full_path(self):
        """Return full hierarchical path including warehouse"""
        base_path = self.unidad_organizacional.get_full_path()
        return f"{base_path} → {self.nombre}"
    
    def get_current_capacity_usage(self):
        """Calculate current capacity usage percentage"""

        return 0
    
    def is_at_capacity(self):
        """Check if warehouse is at maximum capacity"""
        return self.get_current_capacity_usage() >= 100
    
    def get_available_capacity(self):
        """Get remaining capacity"""
        used_percentage = self.get_current_capacity_usage()
        return max(0, self.capacidad_maxima * (100 - used_percentage) / 100)
    
    @classmethod
    def get_by_prefix(cls, prefix):
        """Get warehouse by prefix code"""
        try:
            return cls.objects.get(prefijo=prefix, activo=True)
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_all_active(cls):
        """Get all active warehouses"""
        return cls.objects.filter(activo=True).order_by('prefijo')
    
    @classmethod
    def validate_prefix_uniqueness(cls, prefix, exclude_id=None):
        """Validate that prefix is unique across all warehouses"""
        queryset = cls.objects.filter(prefijo=prefix)
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
        return not queryset.exists()


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




# ============================================================================
# SUBALMACÉN MODEL (Nuevo - Reemplaza Acueducto)
# ============================================================================

class Subalmacen(TimeStampedModel):
    """
    Subalmacén con ubicación geográfica.
    Reemplaza el modelo Acueducto con capacidades geográficas mejoradas.
    """
    nombre = models.CharField(max_length=200, help_text='Nombre del subalmacén')
    codigo = models.CharField(max_length=20, unique=True, help_text='Código único (ej: SUB-ZUL-001)')
    
    sucursal = models.ForeignKey(
        'Sucursal',
        on_delete=models.CASCADE,
        related_name='subalmacenes',
        help_text='Sucursal a la que pertenece'
    )
    
    # Ubicación geográfica
    estado = models.ForeignKey(State, on_delete=models.PROTECT, related_name='subalmacenes')
    municipio = models.ForeignKey(Municipality, on_delete=models.PROTECT, related_name='subalmacenes', null=True, blank=True)
    parroquia = models.ForeignKey(Parish, on_delete=models.PROTECT, related_name='subalmacenes', null=True, blank=True)
    
    direccion = models.TextField(blank=True, help_text='Dirección completa')
    coordenadas_gps = models.CharField(max_length=100, blank=True, help_text='Coordenadas GPS (lat,lng)')
    
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='subalmacenes_responsable')
    capacidad = models.IntegerField(null=True, blank=True, help_text='Capacidad de almacenamiento')
    activo = models.BooleanField(default=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Subalmacén'
        verbose_name_plural = 'Subalmacenes'
        unique_together = ('nombre', 'sucursal')
        ordering = ['estado__name', 'sucursal__nombre', 'nombre']
        indexes = [
            models.Index(fields=['estado', 'activo']),
            models.Index(fields=['sucursal', 'activo']),
            models.Index(fields=['codigo']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({self.estado.name})"
    
    def get_ubicacion_completa(self):
        partes = [self.estado.name]
        if self.municipio:
            partes.append(self.municipio.name)
        if self.parroquia:
            partes.append(self.parroquia.name)
        return ", ".join(partes)
    
    def es_responsable(self, user):
        return self.responsable == user or user.is_staff


# ============================================================================
# LEGACY MODELS (Backward Compatibility)
# ============================================================================

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


# ============================================================================
# MIGRATION SUPPORT MODELS
# ============================================================================

class MigracionOrganizacional(models.Model):
    """
    Mapping between old and new organizational structures for safe migration.
    Tracks migration status and provides rollback capabilities.
    
    This model supports the organizational restructuring by maintaining
    relationships between the old flat structure (OrganizacionCentral, 
    Sucursal, Acueducto) and the new hierarchical structure (Empresa,
    Vicepresidencia, UnidadOrganizacional).
    """
    
    # Old structure references
    organizacion_central_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='ID of the original OrganizacionCentral record'
    )
    sucursal_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='ID of the original Sucursal record'
    )
    acueducto_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='ID of the original Acueducto record'
    )
    
    # New structure references
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='migraciones',
        help_text='Mapped Empresa in new hierarchy'
    )
    vicepresidencia = models.ForeignKey(
        Vicepresidencia,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='migraciones',
        help_text='Mapped Vicepresidencia in new hierarchy'
    )
    unidad_organizacional = models.ForeignKey(
        UnidadOrganizacional,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='migraciones',
        help_text='Mapped UnidadOrganizacional in new hierarchy'
    )
    acueducto_nuevo = models.ForeignKey(
        Subalmacen,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='migraciones',
        help_text='Mapped new Subalmacen in new hierarchy'
    )
    
    # Migration metadata
    fecha_migracion = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when migration was performed'
    )
    estado_migracion = models.CharField(
        max_length=20,
        choices=[
            ('PENDIENTE', 'Pendiente'),
            ('EN_PROCESO', 'En Proceso'),
            ('COMPLETADA', 'Completada'),
            ('FALLIDA', 'Fallida'),
            ('REVERTIDA', 'Revertida'),
        ],
        default='PENDIENTE',
        help_text='Current migration status'
    )
    validado = models.BooleanField(
        default=False,
        help_text='Whether migration has been validated'
    )
    
    # Migration tracking fields
    migrado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='migraciones_realizadas',
        help_text='User who performed the migration'
    )
    validado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='migraciones_validadas',
        help_text='User who validated the migration'
    )
    fecha_validacion = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp when migration was validated'
    )
    
    # Rollback support
    datos_originales = models.JSONField(
        default=dict,
        blank=True,
        help_text='Original data snapshot for rollback capability'
    )
    puede_revertir = models.BooleanField(
        default=True,
        help_text='Whether this migration can be reverted'
    )
    fecha_reversion = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp when migration was reverted'
    )
    revertido_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='migraciones_revertidas',
        help_text='User who reverted the migration'
    )
    
    # Additional metadata
    notas = models.TextField(
        blank=True,
        help_text='Additional notes about the migration'
    )
    errores = models.JSONField(
        default=list,
        blank=True,
        help_text='List of errors encountered during migration'
    )
    warnings = models.JSONField(
        default=list,
        blank=True,
        help_text='List of warnings generated during migration'
    )
    
    # Audit fields
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Migración Organizacional'
        verbose_name_plural = 'Migraciones Organizacionales'
        ordering = ['-fecha_migracion']
        indexes = [
            models.Index(fields=['organizacion_central_id']),
            models.Index(fields=['sucursal_id']),
            models.Index(fields=['acueducto_id']),
            models.Index(fields=['estado_migracion']),
            models.Index(fields=['validado']),
            models.Index(fields=['fecha_migracion']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(
                    organizacion_central_id__isnull=False
                ) | models.Q(
                    sucursal_id__isnull=False
                ) | models.Q(
                    acueducto_id__isnull=False
                ),
                name='at_least_one_old_reference'
            ),
        ]
    
    def __str__(self):
        old_ref = self.get_old_reference_display()
        new_ref = self.get_new_reference_display()
        return f"Migración: {old_ref} → {new_ref}"
    
    def get_old_reference_display(self):
        """Get display name for old structure reference"""
        if self.acueducto_id:
            try:
                acueducto = Acueducto.objects.get(id=self.acueducto_id)
                return f"Acueducto: {acueducto.nombre}"
            except Acueducto.DoesNotExist:
                return f"Acueducto ID: {self.acueducto_id} (eliminado)"
        elif self.sucursal_id:
            try:
                sucursal = Sucursal.objects.get(id=self.sucursal_id)
                return f"Sucursal: {sucursal.nombre}"
            except Sucursal.DoesNotExist:
                return f"Sucursal ID: {self.sucursal_id} (eliminada)"
        elif self.organizacion_central_id:
            try:
                org = OrganizacionCentral.objects.get(id=self.organizacion_central_id)
                return f"Organización: {org.nombre}"
            except OrganizacionCentral.DoesNotExist:
                return f"Organización ID: {self.organizacion_central_id} (eliminada)"
        return "Sin referencia antigua"
    
    def get_new_reference_display(self):
        """Get display name for new structure reference"""
        if self.acueducto_nuevo:
            return f"Acueducto: {self.acueducto_nuevo.nombre}"
        elif self.unidad_organizacional:
            return f"Unidad: {self.unidad_organizacional.nombre}"
        elif self.vicepresidencia:
            return f"VP: {self.vicepresidencia.nombre}"
        elif self.empresa:
            return f"Empresa: {self.empresa.nombre}"
        return "Sin referencia nueva"
    
    def clean(self):
        """Custom validation for migration mapping"""
        from django.core.exceptions import ValidationError
        
        # Validate that at least one old reference exists
        if not any([self.organizacion_central_id, self.sucursal_id, self.acueducto_id]):
            raise ValidationError(
                'Debe especificar al menos una referencia de la estructura antigua'
            )
        
        # Validate that at least one new reference exists for completed migrations
        if self.estado_migracion == 'COMPLETADA':
            if not any([self.empresa, self.vicepresidencia, self.unidad_organizacional, self.acueducto_nuevo]):
                raise ValidationError(
                    'Las migraciones completadas deben tener al menos una referencia nueva'
                )
        
        # Validate validation fields consistency
        if self.validado and not self.validado_por:
            raise ValidationError(
                'Las migraciones validadas deben tener un usuario validador'
            )
        
        if self.fecha_reversion and not self.revertido_por:
            raise ValidationError(
                'Las migraciones revertidas deben tener un usuario que las revirtió'
            )
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def marcar_como_completada(self, usuario=None):
        """Mark migration as completed"""
        self.estado_migracion = 'COMPLETADA'
        if usuario:
            self.migrado_por = usuario
        self.save()
    
    def marcar_como_fallida(self, errores=None):
        """Mark migration as failed with optional error details"""
        self.estado_migracion = 'FALLIDA'
        if errores:
            if isinstance(errores, list):
                self.errores = errores
            else:
                self.errores = [str(errores)]
        self.save()
    
    def validar_migracion(self, usuario):
        """Validate the migration"""
        if self.estado_migracion != 'COMPLETADA':
            raise ValidationError('Solo se pueden validar migraciones completadas')
        
        self.validado = True
        self.validado_por = usuario
        self.fecha_validacion = timezone.now()
        self.save()
    
    def revertir_migracion(self, usuario, motivo=''):
        """Revert the migration if possible"""
        if not self.puede_revertir:
            raise ValidationError('Esta migración no puede ser revertida')
        
        if self.estado_migracion == 'REVERTIDA':
            raise ValidationError('Esta migración ya ha sido revertida')
        
        self.estado_migracion = 'REVERTIDA'
        self.fecha_reversion = timezone.now()
        self.revertido_por = usuario
        if motivo:
            self.notas = f"{self.notas}\n\nRevertida: {motivo}" if self.notas else f"Revertida: {motivo}"
        self.save()
    
    def agregar_warning(self, mensaje):
        """Add a warning message to the migration"""
        if not isinstance(self.warnings, list):
            self.warnings = []
        self.warnings.append({
            'mensaje': mensaje,
            'timestamp': timezone.now().isoformat()
        })
        self.save()
    
    def agregar_error(self, mensaje):
        """Add an error message to the migration"""
        if not isinstance(self.errores, list):
            self.errores = []
        self.errores.append({
            'mensaje': mensaje,
            'timestamp': timezone.now().isoformat()
        })
        self.save()
    
    @classmethod
    def crear_migracion_organizacion(cls, organizacion_central, empresa, usuario):
        """Create migration mapping for OrganizacionCentral to Empresa"""
        return cls.objects.create(
            organizacion_central_id=organizacion_central.id,
            empresa=empresa,
            migrado_por=usuario,
            datos_originales={
                'organizacion_central': {
                    'id': organizacion_central.id,
                    'nombre': organizacion_central.nombre,
                    'rif': organizacion_central.rif,
                    'parent_id': organizacion_central.parent_id if organizacion_central.parent else None,
                }
            }
        )
    
    @classmethod
    def crear_migracion_sucursal(cls, sucursal, vicepresidencia, usuario):
        """Create migration mapping for Sucursal to Vicepresidencia"""
        return cls.objects.create(
            organizacion_central_id=sucursal.organizacion_central.id,
            sucursal_id=sucursal.id,
            empresa=vicepresidencia.empresa,
            vicepresidencia=vicepresidencia,
            migrado_por=usuario,
            datos_originales={
                'sucursal': {
                    'id': sucursal.id,
                    'nombre': sucursal.nombre,
                    'codigo': sucursal.codigo,
                    'direccion': sucursal.direccion,
                    'telefono': sucursal.telefono,
                    'organizacion_central_id': sucursal.organizacion_central.id,
                }
            }
        )
    
    @classmethod
    def crear_migracion_acueducto(cls, acueducto, unidad_organizacional, usuario):
        """Create migration mapping for Acueducto to UnidadOrganizacional"""
        return cls.objects.create(
            organizacion_central_id=acueducto.sucursal.organizacion_central.id,
            sucursal_id=acueducto.sucursal.id,
            acueducto_id=acueducto.id,
            empresa=unidad_organizacional.vicepresidencia.empresa,
            vicepresidencia=unidad_organizacional.vicepresidencia,
            unidad_organizacional=unidad_organizacional,
            migrado_por=usuario,
            datos_originales={
                'acueducto': {
                    'id': acueducto.id,
                    'nombre': acueducto.nombre,
                    'codigo': acueducto.codigo,
                    'ubicacion': acueducto.ubicacion,
                    'sucursal_id': acueducto.sucursal.id,
                }
            }
        )
    
    @classmethod
    def obtener_migraciones_pendientes(cls):
        """Get all pending migrations"""
        return cls.objects.filter(estado_migracion='PENDIENTE')
    
    @classmethod
    def obtener_migraciones_completadas(cls):
        """Get all completed migrations"""
        return cls.objects.filter(estado_migracion='COMPLETADA')
    
    @classmethod
    def obtener_migraciones_fallidas(cls):
        """Get all failed migrations"""
        return cls.objects.filter(estado_migracion='FALLIDA')
    
    @classmethod
    def validar_integridad_migracion(cls):
        """Validate migration integrity across all records"""
        errores = []
        warnings = []
        
        # Check for orphaned old references
        for migracion in cls.objects.filter(estado_migracion='COMPLETADA'):
            if migracion.organizacion_central_id:
                try:
                    OrganizacionCentral.objects.get(id=migracion.organizacion_central_id)
                except OrganizacionCentral.DoesNotExist:
                    warnings.append(f"Migración {migracion.id}: OrganizacionCentral {migracion.organizacion_central_id} no existe")
            
            if migracion.sucursal_id:
                try:
                    Sucursal.objects.get(id=migracion.sucursal_id)
                except Sucursal.DoesNotExist:
                    warnings.append(f"Migración {migracion.id}: Sucursal {migracion.sucursal_id} no existe")
            
            if migracion.acueducto_id:
                try:
                    Acueducto.objects.get(id=migracion.acueducto_id)
                except Acueducto.DoesNotExist:
                    warnings.append(f"Migración {migracion.id}: Acueducto {migracion.acueducto_id} no existe")
        
        return {
            'errores': errores,
            'warnings': warnings,
            'total_migraciones': cls.objects.count(),
            'completadas': cls.objects.filter(estado_migracion='COMPLETADA').count(),
            'pendientes': cls.objects.filter(estado_migracion='PENDIENTE').count(),
            'fallidas': cls.objects.filter(estado_migracion='FALLIDA').count(),
        }


