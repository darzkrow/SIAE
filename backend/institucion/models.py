from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from mptt.models import MPTTModel, TreeForeignKey

User = get_user_model()

# ============================================================================
# NUEVOS MODELOS ORGANIZACIONALES JERÁRQUICOS (MPTT)
# ============================================================================

class Empresa(MPTTModel):
    """
    Root company model - Hidroven
    Uses MPTT for efficient hierarchical operations
    """
    nombre = models.CharField(max_length=200, unique=True)
    codigo = models.CharField(max_length=10, unique=True)
    rif = models.CharField(max_length=30, blank=True, verbose_name='RIF')
    direccion = models.TextField(blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # MPTT fields
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
            models.Index(fields=['fecha_creacion']),
        ]
    
    def __str__(self):
        return self.nombre
    
    def get_full_path(self):
        """Return full hierarchical path"""
        ancestors = self.get_ancestors(include_self=True)
        return ' → '.join([ancestor.nombre for ancestor in ancestors])


class Vicepresidencia(MPTTModel):
    """
    Three VP types: Comercialización, Operaciones Hídricas, Administrativa
    Second level in organizational hierarchy
    """
    VP_TYPES = [
        ('COMERCIALIZACION', 'Vicepresidencia de Comercialización'),
        ('OPERACIONES_HIDRICAS', 'Vicepresidencia de Operaciones Hídricas'),
        ('ADMINISTRATIVA', 'Vicepresidencia Administrativa'),
    ]
    
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='vicepresidencias'
    )
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=50, choices=VP_TYPES)
    descripcion = models.TextField(blank=True)
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vicepresidencias_responsable'
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
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


class UnidadOrganizacional(MPTTModel):
    """
    Generic organizational units under VPs
    Third level in organizational hierarchy
    """
    TIPO_UNIDAD_CHOICES = [
        ('GERENCIA', 'Gerencia'),
        ('COORDINACION', 'Coordinación'),
        ('DEPARTAMENTO', 'Departamento'),
        ('DIVISION', 'División'),
        ('SECCION', 'Sección'),
        ('OFICINA', 'Oficina'),
        ('ALMACEN', 'Almacén'),
        ('PLANTA', 'Planta de Tratamiento'),
        ('ESTACION', 'Estación de Bombeo'),
    ]
    
    vicepresidencia = models.ForeignKey(
        Vicepresidencia,
        on_delete=models.CASCADE,
        related_name='unidades_organizacionales'
    )
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=30, unique=True)
    tipo = models.CharField(max_length=50, choices=TIPO_UNIDAD_CHOICES)
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
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
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


class AlmacenRegional(models.Model):
    """
    9 regional warehouses under VP Operations
    Each warehouse has a unique three-letter prefix code
    """
    # Predefined warehouse prefixes as per requirements
    PREFIJOS_VALIDOS = [
        ('ZUL', 'Zulia'),
        ('CAR', 'Carabobo'),
        ('MIR', 'Miranda'),
        ('ARA', 'Aragua'),
        ('LAR', 'Lara'),
        ('TAC', 'Táchira'),
        ('BOL', 'Bolívar'),
        ('ANZ', 'Anzoátegui'),
        ('MON', 'Monagas'),
    ]
    
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
        choices=PREFIJOS_VALIDOS,
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
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
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
        # This would be implemented when asset tracking is added
        # For now, return 0 as placeholder
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
        'AcueductoNuevo',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='migraciones',
        help_text='Mapped new Acueducto in new hierarchy'
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


# ============================================================================
# ASSET TRACKING MODELS
# ============================================================================

class ActivoInventario(models.Model):
    """
    Individual asset with unique evolving code and complete traceability.
    Each asset has a unique code that evolves with transfers between warehouses.
    
    Asset Code Pattern:
    - Initial: {WAREHOUSE_PREFIX}-{ASSET_TYPE}-{SEQUENCE}-{YEAR}
    - After transfer: {NEW_WAREHOUSE}-{PREVIOUS_CODE}
    
    Example evolution:
    ZUL-BOMBA-000001-2024 → CAR-ZUL-BOMBA-000001-2024 → MIR-CAR-ZUL-BOMBA-000001-2024
    """
    
    # Asset States as per requirements
    ASSET_STATES = [
        ('EN_ALMACEN', 'En Almacén'),
        ('EN_TRANSITO', 'En Tránsito'),
        ('INSTALADO', 'Instalado'),
        ('EN_USO', 'En Uso'),
        ('MANTENIMIENTO', 'En Mantenimiento'),
    ]
    
    # Asset Types for code generation
    ASSET_TYPES = [
        ('BOMBA', 'Bomba'),
        ('MOTOR', 'Motor'),
        ('TUBERIA', 'Tubería'),
        ('QUIMICO', 'Químico'),
        ('ACCESORIO', 'Accesorio'),
        ('EQUIPO', 'Equipo'),
        ('VALVULA', 'Válvula'),
        ('MEDIDOR', 'Medidor'),
    ]
    
    # Unique evolving asset code
    codigo_actual = models.CharField(
        max_length=100,
        unique=True,
        help_text='Código único actual que evoluciona con traslados'
    )
    codigo_original = models.CharField(
        max_length=100,
        help_text='Código original sin prefijos adicionales de traslados'
    )
    
    # Asset classification
    tipo_activo = models.CharField(
        max_length=20,
        choices=ASSET_TYPES,
        help_text='Tipo de activo para generación de código'
    )
    descripcion = models.TextField(
        help_text='Descripción detallada del activo'
    )
    
    # Current location and state
    almacen_actual = models.ForeignKey(
        AlmacenRegional,
        on_delete=models.CASCADE,
        related_name='activos_actuales',
        help_text='Almacén donde se encuentra actualmente'
    )
    estado = models.CharField(
        max_length=20,
        choices=ASSET_STATES,
        default='EN_ALMACEN',
        help_text='Estado actual del activo'
    )
    
    # Asset details
    fecha_ingreso = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de ingreso al sistema'
    )
    valor_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Valor unitario del activo'
    )
    numero_serie = models.CharField(
        max_length=100,
        blank=True,
        help_text='Número de serie del fabricante'
    )
    
    # Relationship to existing inventory models
    # Using ContentType for generic relationship to any product model
    producto_inventario_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text='Tipo de producto del inventario (ChemicalProduct, Pipe, etc.)'
    )
    producto_inventario_id = models.PositiveIntegerField(
        help_text='ID del producto específico en el inventario'
    )
    producto_inventario = GenericForeignKey(
        'producto_inventario_type',
        'producto_inventario_id'
    )
    
    # Audit fields
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='activos_creados',
        null=True,
        blank=True,
        help_text='Usuario que creó el registro del activo'
    )
    actualizado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='activos_actualizados',
        null=True,
        blank=True,
        help_text='Usuario que actualizó por última vez el activo'
    )
    
    class Meta:
        verbose_name = 'Activo de Inventario'
        verbose_name_plural = 'Activos de Inventario'
        ordering = ['-fecha_ingreso']
        indexes = [
            models.Index(fields=['codigo_actual']),
            models.Index(fields=['codigo_original']),
            models.Index(fields=['almacen_actual', 'estado']),
            models.Index(fields=['tipo_activo', 'estado']),
            models.Index(fields=['fecha_ingreso']),
            models.Index(fields=['producto_inventario_type', 'producto_inventario_id']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['codigo_actual'],
                name='unique_activo_codigo_actual'
            ),
        ]
    
    def __str__(self):
        return f"{self.codigo_actual} - {self.get_tipo_activo_display()}"
    
    def clean(self):
        """Custom validation for ActivoInventario"""
        from django.core.exceptions import ValidationError
        from .services import AssetCodeGenerator
        
        # Validate asset code format if provided
        if self.codigo_actual:
            if not AssetCodeGenerator.validate_asset_code_format(self.codigo_actual):
                raise ValidationError({
                    'codigo_actual': 'El código del activo no tiene un formato válido'
                })
        
        # Validate state transitions
        if self.pk:  # Only for existing objects
            try:
                old_instance = ActivoInventario.objects.get(pk=self.pk)
                if not self.is_valid_state_transition(old_instance.estado, self.estado):
                    raise ValidationError({
                        'estado': f'Transición de estado inválida: {old_instance.estado} → {self.estado}'
                    })
            except ActivoInventario.DoesNotExist:
                pass
    
    def save(self, *args, **kwargs):
        """Override save to generate asset code and handle state changes"""
        # Generate asset code if not provided
        if not self.codigo_actual:
            self.codigo_actual = self.generate_asset_code()
            self.codigo_original = self.codigo_actual
        
        # Track state changes for audit
        old_state = None
        if self.pk:
            try:
                old_instance = ActivoInventario.objects.get(pk=self.pk)
                old_state = old_instance.estado
            except ActivoInventario.DoesNotExist:
                pass
        
        # Validate before saving
        self.full_clean()
        
        super().save(*args, **kwargs)
        
        # Create audit record for state changes using state management system
        if old_state and old_state != self.estado:
            self.create_state_change_audit(old_state, self.estado)
    
    def generate_asset_code(self):
        """
        Generate unique asset code using AssetCodeGenerator service.
        """
        from .services import AssetCodeGenerator
        
        return AssetCodeGenerator.generate_asset_code(
            warehouse_prefix=self.almacen_actual.prefijo,
            asset_type=self.tipo_activo
        )
    
    def evolve_asset_code(self, new_warehouse):
        """
        Evolve asset code when transferring to a new warehouse using AssetCodeGenerator service.
        """
        from .services import AssetCodeGenerator
        
        if new_warehouse.prefijo != self.almacen_actual.prefijo:
            old_code = self.codigo_actual
            new_code = AssetCodeGenerator.evolve_asset_code(
                current_code=old_code,
                new_warehouse_prefix=new_warehouse.prefijo
            )
            self.codigo_actual = new_code
            return old_code, new_code
        return self.codigo_actual, self.codigo_actual
    
    @staticmethod
    def validate_asset_code_format(code):
        """
        Validate asset code format using AssetCodeGenerator service.
        """
        from .services import AssetCodeGenerator
        
        return AssetCodeGenerator.validate_asset_code_format(code)
    
    @staticmethod
    def parse_asset_code(code):
        """
        Parse asset code to extract movement history and asset information using AssetCodeGenerator service.
        """
        from .services import AssetCodeGenerator
        
        code_info = AssetCodeGenerator.parse_asset_code(code)
        if not code_info:
            return None
        
        return {
            'current_warehouse': code_info.current_warehouse,
            'movement_history': code_info.movement_history,
            'asset_type': code_info.asset_type,
            'sequence': code_info.sequence,
            'year': code_info.year,
            'original_code': code_info.original_code
        }
    
    def get_movement_history_from_code(self):
        """Extract movement history from current asset code using AssetCodeGenerator service"""
        from .services import AssetCodeGenerator
        
        return AssetCodeGenerator.get_movement_history_from_code(self.codigo_actual)
    
    @staticmethod
    def is_valid_state_transition(from_state, to_state):
        """
        Validate state transitions according to business rules using AssetStateManager.
        """
        from .state_management import AssetStateManager
        
        is_valid, _ = AssetStateManager.validate_state_transition(from_state, to_state)
        return is_valid
    
    def create_state_change_audit(self, old_state, new_state):
        """Create audit record for state changes using AssetStateManager"""
        from .state_management import AssetStateAuditLogger
        
        # Log the state change
        AssetStateAuditLogger.log_state_change_attempt(
            activo=self,
            old_state=old_state,
            new_state=new_state,
            user=self.actualizado_por or self.creado_por,
            success=True
        )
        
        # Create movement record
        HistorialMovimientoActivo.create_movement_record(
            activo=self,
            tipo_movimiento='CAMBIO_ESTADO',
            usuario_responsable=self.actualizado_por or self.creado_por,
            motivo=f'Cambio de estado: {old_state} → {new_state}',
            estado_anterior=old_state,
            estado_nuevo=new_state,
            observaciones=f'Estado actualizado automáticamente'
        )
    
    def get_current_location_display(self):
        """Get human-readable current location"""
        location = f"{self.almacen_actual.nombre} ({self.almacen_actual.prefijo})"
        if self.estado == 'INSTALADO' or self.estado == 'EN_USO':
            # Could be extended to include specific installation location
            location += f" - {self.get_estado_display()}"
        return location
    
    def get_asset_age_days(self):
        """Get asset age in days since ingreso"""
        from django.utils import timezone
        return (timezone.now().date() - self.fecha_ingreso.date()).days
    
    def get_transfer_count(self):
        """Get number of transfers from code evolution using AssetCodeGenerator service"""
        from .services import AssetCodeGenerator
        
        return AssetCodeGenerator.get_transfer_count(self.codigo_actual)
    
    @classmethod
    def get_assets_by_warehouse(cls, warehouse):
        """Get all assets currently in a specific warehouse"""
        return cls.objects.filter(
            almacen_actual=warehouse,
            estado__in=['EN_ALMACEN', 'EN_TRANSITO']
        )
    
    @classmethod
    def get_assets_by_state(cls, state):
        """Get all assets in a specific state"""
        return cls.objects.filter(estado=state)
    
    @classmethod
    def get_assets_by_type(cls, asset_type):
        """Get all assets of a specific type"""
        return cls.objects.filter(tipo_activo=asset_type)
    
    @classmethod
    def validate_code_uniqueness(cls, code, exclude_id=None):
        """Validate that asset code is unique using AssetCodeGenerator service"""
        from .services import AssetCodeGenerator
        
        # First validate format
        if not AssetCodeGenerator.validate_asset_code_format(code):
            return False
        
        # Then check uniqueness in database
        queryset = cls.objects.filter(codigo_actual=code)
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
        return not queryset.exists()
    
    def change_state(self, new_state: str, user, motivo: str, observaciones: str = ''):
        """
        Change asset state using AssetStateManager with validation and audit logging.
        
        Args:
            new_state: Target state
            user: User making the change
            motivo: Reason for state change
            observaciones: Additional observations
            
        Returns:
            bool: True if state change was successful
            
        Raises:
            ValidationError: If state transition is not allowed
        """
        from .state_management import AssetStateManager
        
        return AssetStateManager.change_asset_state(
            activo=self,
            new_state=new_state,
            user=user,
            motivo=motivo,
            observaciones=observaciones
        )
    
    def get_allowed_state_transitions(self):
        """
        Get all allowed state transitions from current state.
        
        Returns:
            List[Tuple[str, str]]: List of (target_state, description) tuples
        """
        from .state_management import AssetStateManager
        
        return AssetStateManager.get_allowed_transitions(self.estado)
    
    def can_be_transferred(self):
        """
        Check if asset can be included in a transfer request.
        
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        from .state_management import AssetStateManager
        
        return AssetStateManager.validate_transfer_request_state(self)
    
    def get_state_history(self, limit: int = 10):
        """
        Get state transition history for this asset.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List[Dict]: List of state transition records
        """
        from .state_management import AssetStateManager
        
        return AssetStateManager.get_state_transition_history(self, limit)


class HistorialMovimientoActivo(models.Model):
    """
    Immutable record of all asset movements and state changes.
    Provides complete audit trail for asset traceability.
    
    Requirements implemented:
    - 6.1: Immutable movement records for complete asset traceability
    - 6.2: Audit models for state changes and approval decisions
    - 6.4: Proper indexing for audit queries and reporting
    - 6.5: Comprehensive audit trail system
    
    This model serves as the primary audit trail for all asset operations,
    ensuring complete traceability from creation to disposal with immutable
    records that cannot be modified after creation.
    """
    
    MOVEMENT_TYPES = [
        ('INGRESO_INICIAL', 'Ingreso Inicial'),
        ('TRASLADO_ALMACEN', 'Traslado entre Almacenes'),
        ('TRASLADO_EJECUTADO', 'Traslado Ejecutado'),
        ('ROLLBACK_TRASLADO', 'Rollback de Traslado'),
        ('CAMBIO_ESTADO', 'Cambio de Estado'),
        ('CAMBIO_ESTADO_AUTO_TRANSFER_APPROVED', 'Cambio de Estado Automático - Traslado Aprobado'),
        ('CAMBIO_ESTADO_AUTO_TRANSFER_COMPLETED', 'Cambio de Estado Automático - Traslado Completado'),
        ('CAMBIO_ESTADO_AUTO_MAINTENANCE_REQUIRED', 'Cambio de Estado Automático - Mantenimiento Requerido'),
        ('INSTALACION', 'Instalación'),
        ('RETIRO', 'Retiro'),
        ('MANTENIMIENTO_ENTRADA', 'Entrada a Mantenimiento'),
        ('MANTENIMIENTO_SALIDA', 'Salida de Mantenimiento'),
        ('CORRECCION_INVENTARIO', 'Corrección de Inventario'),
        ('AUDITORIA_FISICA', 'Auditoría Física'),
        ('BAJA_ACTIVO', 'Baja de Activo'),
        ('REACTIVACION_ACTIVO', 'Reactivación de Activo'),
    ]
    
    # Asset reference
    activo = models.ForeignKey(
        ActivoInventario,
        on_delete=models.CASCADE,
        related_name='historial_movimientos',
        help_text='Activo al que pertenece este movimiento'
    )
    
    # Movement details
    tipo_movimiento = models.CharField(
        max_length=50,
        choices=MOVEMENT_TYPES,
        help_text='Tipo de movimiento realizado'
    )
    fecha_movimiento = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha y hora del movimiento'
    )
    
    # Location changes
    almacen_origen = models.ForeignKey(
        AlmacenRegional,
        on_delete=models.CASCADE,
        related_name='movimientos_origen',
        null=True,
        blank=True,
        help_text='Almacén de origen (si aplica)'
    )
    almacen_destino = models.ForeignKey(
        AlmacenRegional,
        on_delete=models.CASCADE,
        related_name='movimientos_destino',
        null=True,
        blank=True,
        help_text='Almacén de destino (si aplica)'
    )
    
    # State changes
    estado_anterior = models.CharField(
        max_length=20,
        choices=ActivoInventario.ASSET_STATES,
        help_text='Estado anterior del activo'
    )
    estado_nuevo = models.CharField(
        max_length=20,
        choices=ActivoInventario.ASSET_STATES,
        help_text='Estado nuevo del activo'
    )
    
    # Code evolution
    codigo_anterior = models.CharField(
        max_length=100,
        help_text='Código anterior del activo'
    )
    codigo_nuevo = models.CharField(
        max_length=100,
        help_text='Código nuevo del activo'
    )
    
    # Responsible users
    usuario_responsable = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='movimientos_responsable',
        help_text='Usuario responsable del movimiento'
    )
    
    # Movement details
    motivo = models.TextField(
        help_text='Motivo del movimiento'
    )
    observaciones = models.TextField(
        blank=True,
        help_text='Observaciones adicionales'
    )
    
    # Transfer request reference (if applicable)
    solicitud_traslado = models.ForeignKey(
        'SolicitudTraslado',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='movimientos_asociados',
        help_text='Solicitud de traslado asociada (si aplica)'
    )
    
    # Additional metadata for complex operations
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional metadata for the movement operation'
    )
    
    class Meta:
        verbose_name = 'Historial de Movimiento de Activo'
        verbose_name_plural = 'Historial de Movimientos de Activos'
        ordering = ['-fecha_movimiento']
        indexes = [
            # Primary audit trail indexes for efficient queries
            models.Index(fields=['activo', '-fecha_movimiento'], name='idx_hist_activo_fecha'),
            models.Index(fields=['almacen_origen', '-fecha_movimiento'], name='idx_hist_origen_fecha'),
            models.Index(fields=['almacen_destino', '-fecha_movimiento'], name='idx_hist_destino_fecha'),
            models.Index(fields=['tipo_movimiento', '-fecha_movimiento'], name='idx_hist_tipo_fecha'),
            models.Index(fields=['usuario_responsable', '-fecha_movimiento'], name='idx_hist_usuario_fecha'),
            
            # Composite indexes for complex audit queries
            models.Index(fields=['activo', 'tipo_movimiento', '-fecha_movimiento'], name='idx_hist_activo_tipo_fecha'),
            models.Index(fields=['almacen_origen', 'almacen_destino', '-fecha_movimiento'], name='idx_hist_orig_dest_fecha'),
            models.Index(fields=['estado_anterior', 'estado_nuevo', '-fecha_movimiento'], name='idx_hist_estados_fecha'),
            
            # Reporting and analytics indexes
            models.Index(fields=['fecha_movimiento'], name='idx_hist_fecha_only'),
            models.Index(fields=['solicitud_traslado', '-fecha_movimiento'], name='idx_hist_solicitud_fecha'),
            
            # Performance indexes for audit trail queries
            models.Index(fields=['activo', 'almacen_origen', '-fecha_movimiento'], name='idx_hist_act_orig_fecha'),
            models.Index(fields=['activo', 'almacen_destino', '-fecha_movimiento'], name='idx_hist_act_dest_fecha'),
            models.Index(fields=['tipo_movimiento', 'estado_nuevo', '-fecha_movimiento'], name='idx_hist_tipo_est_fecha'),
        ]
        constraints = [
            # Ensure immutability by preventing updates
            models.CheckConstraint(
                check=models.Q(fecha_movimiento__isnull=False),
                name='historial_fecha_movimiento_required'
            ),
        ]
    
    def __str__(self):
        return f"{self.activo.codigo_actual} - {self.get_tipo_movimiento_display()} - {self.fecha_movimiento.strftime('%Y-%m-%d %H:%M')}"
    
    def clean(self):
        """Custom validation for movement records"""
        from django.core.exceptions import ValidationError
        
        # Validate that movement type matches the state/location changes
        if self.tipo_movimiento == 'TRASLADO_ALMACEN':
            if not (self.almacen_origen and self.almacen_destino):
                raise ValidationError(
                    'Los traslados entre almacenes requieren almacén origen y destino'
                )
            if self.almacen_origen == self.almacen_destino:
                raise ValidationError(
                    'El almacén origen y destino no pueden ser el mismo'
                )
        
        # Validate state transitions
        if not ActivoInventario.is_valid_state_transition(self.estado_anterior, self.estado_nuevo):
            raise ValidationError(
                f'Transición de estado inválida: {self.estado_anterior} → {self.estado_nuevo}'
            )
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure validation and immutability.
        
        Implements requirement 6.1: Immutable movement records for complete asset traceability
        """
        # Prevent modification of existing records (immutable audit trail)
        if self.pk:
            raise ValidationError(
                'Los registros de historial de movimientos son inmutables y no pueden ser modificados. '
                'Para corregir errores, cree un nuevo registro de corrección.'
            )
        
        # Ensure required fields are present
        if not self.activo:
            raise ValidationError('El activo es requerido para el historial de movimientos')
        
        if not self.usuario_responsable:
            raise ValidationError('El usuario responsable es requerido para el historial de movimientos')
        
        # Validate movement type consistency
        self.full_clean()
        
        # Set immutable timestamp if not already set
        if not self.fecha_movimiento:
            from django.utils import timezone
            self.fecha_movimiento = timezone.now()
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """
        Override delete to prevent deletion of audit records.
        
        Implements requirement 6.5: Comprehensive audit trail system with immutable records
        """
        raise ValidationError(
            'Los registros de auditoría no pueden ser eliminados. '
            'Los registros de historial de movimientos son inmutables para garantizar la integridad del audit trail.'
        )
    
    @classmethod
    def create_movement_record(cls, activo, tipo_movimiento, usuario_responsable, 
                             motivo, almacen_origen=None, almacen_destino=None,
                             estado_anterior=None, estado_nuevo=None,
                             observaciones='', solicitud_traslado=None, metadata=None):
        """
        Create a new movement record with proper validation.
        """
        # Get current state if not provided
        if estado_anterior is None:
            estado_anterior = activo.estado
        if estado_nuevo is None:
            estado_nuevo = activo.estado
        
        if metadata is None:
            metadata = {}
        
        return cls.objects.create(
            activo=activo,
            tipo_movimiento=tipo_movimiento,
            almacen_origen=almacen_origen,
            almacen_destino=almacen_destino,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            codigo_anterior=activo.codigo_actual,
            codigo_nuevo=activo.codigo_actual,  # Will be updated if code changes
            usuario_responsable=usuario_responsable,
            motivo=motivo,
            observaciones=observaciones,
            solicitud_traslado=solicitud_traslado,
            metadata=metadata
        )
    
    def get_movement_summary(self):
        """Get a human-readable summary of the movement"""
        summary = f"{self.get_tipo_movimiento_display()}"
        
        if self.almacen_origen and self.almacen_destino:
            summary += f" de {self.almacen_origen.prefijo} a {self.almacen_destino.prefijo}"
        elif self.almacen_destino:
            summary += f" a {self.almacen_destino.prefijo}"
        elif self.almacen_origen:
            summary += f" desde {self.almacen_origen.prefijo}"
        
        if self.estado_anterior != self.estado_nuevo:
            summary += f" (Estado: {self.estado_anterior} → {self.estado_nuevo})"
        
        return summary


class SolicitudTraslado(models.Model):
    """
    Transfer request with dual approval workflow.
    Manages the complete process from request to execution.
    """
    
    TRANSFER_STATES = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADA_ORIGEN', 'Aprobada por Origen'),
        ('APROBADA_DESTINO', 'Aprobada por Destino'),
        ('APROBADA_COMPLETA', 'Completamente Aprobada'),
        ('EN_TRANSITO', 'En Tránsito'),
        ('COMPLETADA', 'Completada'),
        ('RECHAZADA', 'Rechazada'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    PRIORITY_LEVELS = [
        ('BAJA', 'Baja'),
        ('NORMAL', 'Normal'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]
    
    # Basic information
    numero_solicitud = models.CharField(
        max_length=20,
        unique=True,
        help_text='Número único de la solicitud'
    )
    fecha_solicitud = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de creación de la solicitud'
    )
    estado = models.CharField(
        max_length=20,
        choices=TRANSFER_STATES,
        default='PENDIENTE',
        help_text='Estado actual de la solicitud'
    )
    
    # Asset to transfer
    activo = models.ForeignKey(
        ActivoInventario,
        on_delete=models.CASCADE,
        related_name='solicitudes_traslado',
        help_text='Activo a trasladar'
    )
    
    # Warehouses
    almacen_origen = models.ForeignKey(
        AlmacenRegional,
        on_delete=models.CASCADE,
        related_name='solicitudes_origen',
        help_text='Almacén de origen'
    )
    almacen_destino = models.ForeignKey(
        AlmacenRegional,
        on_delete=models.CASCADE,
        related_name='solicitudes_destino',
        help_text='Almacén de destino'
    )
    
    # Request details
    solicitante = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='solicitudes_traslado_realizadas',
        help_text='Usuario que solicita el traslado'
    )
    motivo = models.TextField(
        help_text='Motivo del traslado'
    )
    fecha_limite = models.DateTimeField(
        help_text='Fecha límite para completar el traslado'
    )
    prioridad = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default='NORMAL',
        help_text='Prioridad de la solicitud'
    )
    
    # Approval tracking
    aprobacion_origen = models.ForeignKey(
        'AprobacionTraslado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_origen',
        help_text='Aprobación del almacén origen'
    )
    aprobacion_destino = models.ForeignKey(
        'AprobacionTraslado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_destino',
        help_text='Aprobación del almacén destino'
    )
    
    # Execution tracking
    fecha_ejecucion = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha de ejecución del traslado'
    )
    ejecutado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='traslados_ejecutados',
        help_text='Usuario que ejecutó el traslado'
    )
    fecha_completada = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha de finalización del traslado'
    )
    
    # Additional information
    observaciones = models.TextField(
        blank=True,
        help_text='Observaciones adicionales'
    )
    
    class Meta:
        verbose_name = 'Solicitud de Traslado'
        verbose_name_plural = 'Solicitudes de Traslado'
        ordering = ['-fecha_solicitud']
        indexes = [
            models.Index(fields=['estado', '-fecha_solicitud']),
            models.Index(fields=['almacen_origen', 'estado']),
            models.Index(fields=['almacen_destino', 'estado']),
            models.Index(fields=['solicitante', '-fecha_solicitud']),
            models.Index(fields=['prioridad', '-fecha_solicitud']),
            # Additional indexes for manager dashboard queries
            models.Index(fields=['almacen_origen', 'estado', '-fecha_solicitud']),
            models.Index(fields=['almacen_destino', 'estado', '-fecha_solicitud']),
            models.Index(fields=['fecha_limite', 'estado']),
            models.Index(fields=['prioridad', 'estado', '-fecha_solicitud']),
            # Composite indexes for approval workflow
            models.Index(fields=['aprobacion_origen', 'estado']),
            models.Index(fields=['aprobacion_destino', 'estado']),
            models.Index(fields=['estado', 'fecha_limite']),
        ]
    
    def __str__(self):
        return f"{self.numero_solicitud} - {self.activo.codigo_actual} ({self.almacen_origen.prefijo} → {self.almacen_destino.prefijo})"
    
    def clean(self):
        """Custom validation for transfer requests"""
        from django.core.exceptions import ValidationError
        from .state_management import AssetStateManager
        
        # Validate that origin and destination are different
        if self.almacen_origen == self.almacen_destino:
            raise ValidationError(
                'El almacén origen y destino no pueden ser el mismo'
            )
        
        # Validate that asset is currently in origin warehouse
        if self.activo and self.activo.almacen_actual != self.almacen_origen:
            raise ValidationError(
                f'El activo no se encuentra en el almacén origen especificado. '
                f'Ubicación actual: {self.activo.almacen_actual.prefijo}'
            )
        
        # Validate asset state for transfer using state management system
        if self.activo:
            can_transfer, message = AssetStateManager.validate_transfer_request_state(self.activo)
            if not can_transfer:
                raise ValidationError(f'Estado del activo no permite traslado: {message}')
        
        # Validate workflow state consistency
        self.validate_workflow_state_consistency()
    
    def validate_workflow_state_consistency(self):
        """Validate that workflow state is consistent with approvals"""
        from django.core.exceptions import ValidationError
        
        approval_status = self.get_approval_status()
        
        # Check state consistency
        if self.estado == 'APROBADA_COMPLETA':
            if not (approval_status['origen_aprobado'] and approval_status['destino_aprobado']):
                raise ValidationError(
                    'Estado APROBADA_COMPLETA requiere ambas aprobaciones'
                )
        
        elif self.estado == 'APROBADA_ORIGEN':
            if not approval_status['origen_aprobado'] or approval_status['destino_aprobado']:
                raise ValidationError(
                    'Estado APROBADA_ORIGEN requiere solo aprobación de origen'
                )
        
        elif self.estado == 'APROBADA_DESTINO':
            if not approval_status['destino_aprobado'] or approval_status['origen_aprobado']:
                raise ValidationError(
                    'Estado APROBADA_DESTINO requiere solo aprobación de destino'
                )
        
        elif self.estado == 'RECHAZADA':
            if not approval_status['rechazado']:
                raise ValidationError(
                    'Estado RECHAZADA requiere al menos una aprobación rechazada'
                )
    
    def enforce_dual_approval_workflow(self):
        """Enforce dual approval workflow rules"""
        from django.core.exceptions import ValidationError
        
        # Cannot execute without both approvals
        if self.estado == 'EN_TRANSITO' or self.fecha_ejecucion:
            if not self.can_execute():
                raise ValidationError(
                    'No se puede ejecutar el traslado sin ambas aprobaciones'
                )
        
        # Cannot complete without execution
        if self.estado == 'COMPLETADA' or self.fecha_completada:
            if not self.fecha_ejecucion:
                raise ValidationError(
                    'No se puede completar el traslado sin haberlo ejecutado'
                )
        
        # Validate approval authority
        if self.aprobacion_origen:
            if self.aprobacion_origen.aprobador != self.almacen_origen.manager:
                raise ValidationError(
                    'Solo el gerente del almacén origen puede aprobar desde origen'
                )
        
        if self.aprobacion_destino:
            if self.aprobacion_destino.aprobador != self.almacen_destino.manager:
                raise ValidationError(
                    'Solo el gerente del almacén destino puede aprobar desde destino'
                )
    
    def validate_business_rules(self):
        """Validate additional business rules"""
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        
        # Validate deadline is in the future for new requests
        if not self.pk and self.fecha_limite <= timezone.now():
            raise ValidationError(
                'La fecha límite debe ser en el futuro'
            )
        
        # Validate warehouse managers exist
        if not self.almacen_origen.manager:
            raise ValidationError(
                f'El almacén origen {self.almacen_origen.prefijo} no tiene gerente asignado'
            )
        
        if not self.almacen_destino.manager:
            raise ValidationError(
                f'El almacén destino {self.almacen_destino.prefijo} no tiene gerente asignado'
            )
        
        # Validate warehouse capacity (if implemented)
        if hasattr(self.almacen_destino, 'is_at_capacity') and self.almacen_destino.is_at_capacity():
            if self.prioridad not in ['ALTA', 'URGENTE']:
                raise ValidationError(
                    f'El almacén destino {self.almacen_destino.prefijo} está at capacidad máxima. '
                    'Solo se permiten traslados de alta prioridad.'
                )
    
    def save(self, *args, **kwargs):
        """Override save to generate request number, validate, and enforce workflow"""
        if not self.numero_solicitud:
            self.numero_solicitud = self.generate_request_number()
        
        # Validate all business rules
        self.full_clean()
        self.enforce_dual_approval_workflow()
        self.validate_business_rules()
        
        super().save(*args, **kwargs)
    
    def generate_request_number(self):
        """Generate unique request number"""
        from django.utils import timezone
        
        year = timezone.now().year
        month = timezone.now().month
        
        # Count requests for this month
        count = SolicitudTraslado.objects.filter(
            fecha_solicitud__year=year,
            fecha_solicitud__month=month
        ).count() + 1
        
        return f"ST-{year}{month:02d}-{count:04d}"
    
    def can_approve_origin(self, user):
        """Check if user can approve from origin warehouse"""
        return (self.estado == 'PENDIENTE' and 
                self.almacen_origen.manager == user)
    
    def can_approve_destination(self, user):
        """Check if user can approve from destination warehouse"""
        return (self.estado in ['PENDIENTE', 'APROBADA_ORIGEN'] and 
                self.almacen_destino.manager == user)
    
    def can_execute(self):
        """Check if transfer can be executed"""
        return (self.estado == 'APROBADA_COMPLETA' and 
                self.aprobacion_origen and 
                self.aprobacion_destino and
                self.aprobacion_origen.decision == 'APROBADO' and
                self.aprobacion_destino.decision == 'APROBADO')
    
    def get_approval_status(self):
        """Get detailed approval status"""
        status = {
            'origen_aprobado': False,
            'destino_aprobado': False,
            'completamente_aprobado': False,
            'rechazado': False,
            'pendiente_origen': True,
            'pendiente_destino': True,
        }
        
        if self.aprobacion_origen:
            status['pendiente_origen'] = False
            if self.aprobacion_origen.decision == 'APROBADO':
                status['origen_aprobado'] = True
            elif self.aprobacion_origen.decision == 'RECHAZADO':
                status['rechazado'] = True
        
        if self.aprobacion_destino:
            status['pendiente_destino'] = False
            if self.aprobacion_destino.decision == 'APROBADO':
                status['destino_aprobado'] = True
            elif self.aprobacion_destino.decision == 'RECHAZADO':
                status['rechazado'] = True
        
        status['completamente_aprobado'] = (
            status['origen_aprobado'] and status['destino_aprobado']
        )
        
        return status
    
    def update_workflow_state(self):
        """Update workflow state based on approvals"""
        approval_status = self.get_approval_status()
        
        if approval_status['rechazado']:
            self.estado = 'RECHAZADA'
        elif approval_status['completamente_aprobado']:
            self.estado = 'APROBADA_COMPLETA'
        elif approval_status['origen_aprobado'] and not approval_status['destino_aprobado']:
            self.estado = 'APROBADA_ORIGEN'
        elif approval_status['destino_aprobado'] and not approval_status['origen_aprobado']:
            self.estado = 'APROBADA_DESTINO'
        else:
            self.estado = 'PENDIENTE'
        
        self.save()
    
    def get_pending_approvers(self):
        """Get list of users who still need to approve"""
        pending = []
        approval_status = self.get_approval_status()
        
        if approval_status['pendiente_origen'] and self.almacen_origen.manager:
            pending.append({
                'user': self.almacen_origen.manager,
                'type': 'ORIGEN',
                'warehouse': self.almacen_origen
            })
        
        if approval_status['pendiente_destino'] and self.almacen_destino.manager:
            pending.append({
                'user': self.almacen_destino.manager,
                'type': 'DESTINO', 
                'warehouse': self.almacen_destino
            })
        
        return pending
    
    def get_workflow_timeline(self):
        """Get chronological timeline of workflow events"""
        timeline = []
        
        # Request creation
        timeline.append({
            'fecha': self.fecha_solicitud,
            'evento': 'Solicitud Creada',
            'usuario': self.solicitante,
            'descripcion': f'Solicitud de traslado creada: {self.activo.codigo_actual}'
        })
        
        # Approvals
        if self.aprobacion_origen:
            timeline.append({
                'fecha': self.aprobacion_origen.fecha_decision,
                'evento': f'Aprobación Origen - {self.aprobacion_origen.get_decision_display()}',
                'usuario': self.aprobacion_origen.aprobador,
                'descripcion': self.aprobacion_origen.comentarios or 'Sin comentarios'
            })
        
        if self.aprobacion_destino:
            timeline.append({
                'fecha': self.aprobacion_destino.fecha_decision,
                'evento': f'Aprobación Destino - {self.aprobacion_destino.get_decision_display()}',
                'usuario': self.aprobacion_destino.aprobador,
                'descripcion': self.aprobacion_destino.comentarios or 'Sin comentarios'
            })
        
        # Execution
        if self.fecha_ejecucion:
            timeline.append({
                'fecha': self.fecha_ejecucion,
                'evento': 'Traslado Ejecutado',
                'usuario': self.ejecutado_por,
                'descripcion': 'Traslado iniciado'
            })
        
        # Completion
        if self.fecha_completada:
            timeline.append({
                'fecha': self.fecha_completada,
                'evento': 'Traslado Completado',
                'usuario': self.ejecutado_por,
                'descripcion': 'Traslado finalizado exitosamente'
            })
        
        # Sort by date
        timeline.sort(key=lambda x: x['fecha'])
        return timeline
    
    def is_overdue(self):
        """Check if request is overdue"""
        from django.utils import timezone
        return (self.fecha_limite < timezone.now() and 
                self.estado not in ['COMPLETADA', 'RECHAZADA', 'CANCELADA'])
    
    def get_days_until_deadline(self):
        """Get days until deadline (negative if overdue)"""
        from django.utils import timezone
        delta = self.fecha_limite - timezone.now()
        return delta.days
    
    def can_be_cancelled(self):
        """Check if request can be cancelled"""
        return self.estado in ['PENDIENTE', 'APROBADA_ORIGEN', 'APROBADA_DESTINO']
    
    def cancel_request(self, user, motivo):
        """Cancel the transfer request"""
        if not self.can_be_cancelled():
            raise ValidationError('Esta solicitud no puede ser cancelada en su estado actual')
        
        self.estado = 'CANCELADA'
        self.observaciones = f"{self.observaciones}\n\nCancelada por {user.username}: {motivo}".strip()
        self.save()
        
        # Create audit record
        from .models import HistorialMovimientoActivo
        HistorialMovimientoActivo.create_movement_record(
            activo=self.activo,
            tipo_movimiento='CAMBIO_ESTADO',
            usuario_responsable=user,
            motivo=f'Solicitud de traslado cancelada: {self.numero_solicitud}',
            observaciones=motivo,
            solicitud_traslado=self
        )
    
    @classmethod
    def get_pending_for_manager(cls, manager_user):
        """Get pending requests for a specific manager"""
        from django.db.models import Q
        
        return cls.objects.filter(
            Q(almacen_origen__manager=manager_user, aprobacion_origen__isnull=True) |
            Q(almacen_destino__manager=manager_user, aprobacion_destino__isnull=True),
            estado__in=['PENDIENTE', 'APROBADA_ORIGEN', 'APROBADA_DESTINO']
        ).select_related(
            'activo', 'almacen_origen', 'almacen_destino', 'solicitante'
        ).prefetch_related(
            'aprobaciones'
        )
    
    @classmethod
    def get_dashboard_stats_for_manager(cls, manager_user):
        """Get dashboard statistics for a manager"""
        from django.db.models import Q, Count
        from django.utils import timezone
        
        # Base queryset for this manager's warehouses
        manager_requests = cls.objects.filter(
            Q(almacen_origen__manager=manager_user) |
            Q(almacen_destino__manager=manager_user)
        )
        
        # Pending approvals for this manager
        pending_approvals = cls.objects.filter(
            Q(almacen_origen__manager=manager_user, aprobacion_origen__isnull=True) |
            Q(almacen_destino__manager=manager_user, aprobacion_destino__isnull=True),
            estado__in=['PENDIENTE', 'APROBADA_ORIGEN', 'APROBADA_DESTINO']
        ).count()
        
        # Overdue requests
        overdue_requests = manager_requests.filter(
            fecha_limite__lt=timezone.now(),
            estado__in=['PENDIENTE', 'APROBADA_ORIGEN', 'APROBADA_DESTINO', 'APROBADA_COMPLETA']
        ).count()
        
        # Recent activity (last 7 days)
        week_ago = timezone.now() - timezone.timedelta(days=7)
        recent_activity = manager_requests.filter(
            fecha_solicitud__gte=week_ago
        ).count()
        
        # Status breakdown
        status_counts = manager_requests.values('estado').annotate(
            count=Count('id')
        ).order_by('estado')
        
        return {
            'pending_approvals': pending_approvals,
            'overdue_requests': overdue_requests,
            'recent_activity': recent_activity,
            'total_requests': manager_requests.count(),
            'status_breakdown': {item['estado']: item['count'] for item in status_counts}
        }
    
    @classmethod
    def get_high_priority_requests(cls, manager_user=None):
        """Get high priority requests, optionally filtered by manager"""
        queryset = cls.objects.filter(
            prioridad__in=['ALTA', 'URGENTE'],
            estado__in=['PENDIENTE', 'APROBADA_ORIGEN', 'APROBADA_DESTINO', 'APROBADA_COMPLETA']
        )
        
        if manager_user:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(almacen_origen__manager=manager_user) |
                Q(almacen_destino__manager=manager_user)
            )
        
        return queryset.select_related(
            'activo', 'almacen_origen', 'almacen_destino', 'solicitante'
        ).order_by('-prioridad', 'fecha_limite')
    
    def approve_origin(self, approver, comments=''):
        """Approve transfer from origin warehouse"""
        if not self.can_approve_origin(approver):
            raise ValidationError('No se puede aprobar desde el almacén origen')
        
        # Create or update approval record
        approval, created = AprobacionTraslado.objects.get_or_create(
            solicitud=self,
            tipo_aprobacion='ORIGEN',
            defaults={
                'aprobador': approver,
                'decision': 'APROBADO',
                'comentarios': comments
            }
        )
        
        if not created:
            approval.aprobador = approver
            approval.decision = 'APROBADO'
            approval.comentarios = comments
            approval.save()
        
        self.aprobacion_origen = approval
        
        # Update state based on destination approval status
        if self.aprobacion_destino and self.aprobacion_destino.decision == 'APROBADO':
            self.estado = 'APROBADA_COMPLETA'
        else:
            self.estado = 'APROBADA_ORIGEN'
        
        self.save()
    
    def approve_destination(self, approver, comments=''):
        """Approve transfer from destination warehouse"""
        if not self.can_approve_destination(approver):
            raise ValidationError('No se puede aprobar desde el almacén destino')
        
        # Create or update approval record
        approval, created = AprobacionTraslado.objects.get_or_create(
            solicitud=self,
            tipo_aprobacion='DESTINO',
            defaults={
                'aprobador': approver,
                'decision': 'APROBADO',
                'comentarios': comments
            }
        )
        
        if not created:
            approval.aprobador = approver
            approval.decision = 'APROBADO'
            approval.comentarios = comments
            approval.save()
        
        self.aprobacion_destino = approval
        
        # Update state based on origin approval status
        if self.aprobacion_origen and self.aprobacion_origen.decision == 'APROBADO':
            self.estado = 'APROBADA_COMPLETA'
        else:
            self.estado = 'APROBADA_DESTINO'
        
        self.save()
    
    def reject(self, rejector, reason):
        """Reject transfer request"""
        # Determine rejection type
        if rejector == self.almacen_origen.manager:
            tipo_aprobacion = 'ORIGEN'
        elif rejector == self.almacen_destino.manager:
            tipo_aprobacion = 'DESTINO'
        else:
            raise ValidationError('Solo los gerentes de almacén pueden rechazar solicitudes')
        
        # Create rejection record
        AprobacionTraslado.objects.create(
            solicitud=self,
            tipo_aprobacion=tipo_aprobacion,
            aprobador=rejector,
            decision='RECHAZADO',
            comentarios=reason
        )
        
        self.estado = 'RECHAZADA'
        self.save()
    
    @transaction.atomic
    def execute_transfer(self, executor):
        """
        Execute the approved transfer with atomic operations and comprehensive error handling.
        
        This method implements:
        - Atomic transfer execution with proper transaction management
        - Asset code evolution with rollback capability
        - Inventory synchronization with warehouse counts
        - Integration with existing inventory system
        - Comprehensive error handling and logging
        
        Requirements implemented:
        - 4.4: Transfer execution with asset code evolution
        - 4.7: Atomic transfer execution
        - 7.1: Inventory synchronization with warehouse counts
        - 7.2: Rollback capability for failed transfers
        - 7.3: Integration with existing systems
        
        Args:
            executor: User executing the transfer
            
        Raises:
            ValidationError: If transfer cannot be executed
            Exception: For any other execution errors
        """
        import logging
        from django.utils import timezone
        from django.db import transaction
        from .state_management import AssetStateManager
        from .services import InventorySynchronizationService, AuditTrailService
        
        logger = logging.getLogger(__name__)
        
        # Validate execution preconditions
        if not self.can_execute():
            raise ValidationError('La solicitud no puede ser ejecutada - faltan aprobaciones o estado inválido')
        
        # Store rollback data before making any changes
        rollback_data = self._create_rollback_snapshot()
        execution_start_time = timezone.now()
        
        try:
            # Log transfer execution start
            logger.info(
                f"Starting transfer execution: {self.numero_solicitud} "
                f"for asset {self.activo.codigo_actual} by {executor.username}"
            )
            
            # 1. Validate asset state and location before execution
            self._validate_pre_execution_state()
            
            # 2. Update asset code with evolution (atomic operation)
            old_code, new_code = self._execute_asset_code_evolution()
            
            # 3. Update asset location and state atomically
            self._execute_asset_location_update()
            
            # 4. Handle state change using state management system
            AssetStateManager.handle_transfer_state_changes(
                solicitud_traslado=self,
                stage='approved',
                user=executor
            )
            
            # 5. Synchronize inventory counts with warehouse systems
            sync_result = self._execute_inventory_synchronization(executor)
            if not sync_result.success:
                raise ValidationError(f"Inventory synchronization failed: {sync_result.message}")
            
            # 6. Create comprehensive movement audit record
            self._create_transfer_execution_audit_record(executor, old_code, new_code)
            
            # 7. Update request status and execution metadata
            self._update_execution_status(executor)
            
            # 8. Validate post-execution state
            self._validate_post_execution_state()
            
            # 9. Record comprehensive audit trail
            execution_duration = (timezone.now() - execution_start_time).total_seconds()
            AuditTrailService.record_system_operation(
                accion='TRANSFER_EXECUTION',
                descripcion=f'Transfer execution completed: {self.numero_solicitud}',
                user=executor,
                entidades_afectadas=[
                    {'type': 'ActivoInventario', 'id': self.activo.id, 'codigo': new_code},
                    {'type': 'AlmacenRegional', 'id': self.almacen_origen.id, 'prefijo': self.almacen_origen.prefijo},
                    {'type': 'AlmacenRegional', 'id': self.almacen_destino.id, 'prefijo': self.almacen_destino.prefijo}
                ],
                parametros_operacion={
                    'solicitud_id': self.id,
                    'asset_code_evolution': {'old': old_code, 'new': new_code},
                    'inventory_sync': sync_result.__dict__,
                    'execution_duration_seconds': execution_duration
                },
                exitosa=True,
                duracion_segundos=execution_duration,
                registros_procesados=1,
                puede_revertir=True,
                datos_rollback=rollback_data
            )
            
            # Log successful execution
            logger.info(
                f"Transfer execution completed successfully: {self.numero_solicitud} "
                f"Asset {old_code} -> {new_code} in {execution_duration:.2f}s"
            )
            
        except Exception as e:
            # Log the error
            logger.error(
                f"Transfer execution failed for {self.numero_solicitud}: {str(e)}"
            )
            
            # Record failed execution in audit trail
            execution_duration = (timezone.now() - execution_start_time).total_seconds()
            try:
                AuditTrailService.record_system_operation(
                    accion='TRANSFER_EXECUTION',
                    descripcion=f'Transfer execution failed: {self.numero_solicitud}',
                    user=executor,
                    entidades_afectadas=[
                        {'type': 'ActivoInventario', 'id': self.activo.id, 'codigo': self.activo.codigo_actual},
                        {'type': 'SolicitudTraslado', 'id': self.id, 'numero': self.numero_solicitud}
                    ],
                    parametros_operacion={
                        'solicitud_id': self.id,
                        'error_message': str(e),
                        'execution_duration_seconds': execution_duration
                    },
                    exitosa=False,
                    errores=[str(e)],
                    duracion_segundos=execution_duration,
                    registros_procesados=0,
                    puede_revertir=True,
                    datos_rollback=rollback_data
                )
            except Exception as audit_error:
                logger.error(f"Failed to record execution failure in audit trail: {str(audit_error)}")
            
            # Attempt rollback
            try:
                self._rollback_transfer_execution(rollback_data, executor)
                logger.info(f"Transfer execution rollback completed for {self.numero_solicitud}")
            except Exception as rollback_error:
                logger.error(
                    f"CRITICAL: Failed to rollback transfer execution for {self.numero_solicitud}: "
                    f"{str(rollback_error)}"
                )
                # Re-raise original error with rollback failure info
                raise ValidationError(
                    f"Transfer execution failed and rollback also failed. "
                    f"Original error: {str(e)}. Rollback error: {str(rollback_error)}. "
                    f"Manual intervention required."
                )
            
            # Re-raise the original error
            raise ValidationError(f"Transfer execution failed: {str(e)}")
    
    def _create_rollback_snapshot(self):
        """Create a snapshot of current state for rollback capability"""
        from django.utils import timezone
        
        return {
            'timestamp': timezone.now().isoformat(),
            'solicitud_id': self.id,
            'solicitud_estado': self.estado,
            'solicitud_fecha_ejecucion': self.fecha_ejecucion,
            'solicitud_ejecutado_por': self.ejecutado_por_id if self.ejecutado_por else None,
            'activo_id': self.activo.id,
            'activo_codigo_actual': self.activo.codigo_actual,
            'activo_almacen_actual': self.activo.almacen_actual.id,
            'activo_estado': self.activo.estado,
            'almacen_origen_id': self.almacen_origen.id,
            'almacen_destino_id': self.almacen_destino.id,
        }
    
    def _validate_pre_execution_state(self):
        """Validate state before execution"""
        from django.core.exceptions import ValidationError
        
        # Verify asset is still in origin warehouse
        if self.activo.almacen_actual != self.almacen_origen:
            raise ValidationError(
                f"Asset {self.activo.codigo_actual} is no longer in origin warehouse "
                f"{self.almacen_origen.prefijo}. Current location: {self.activo.almacen_actual.prefijo}"
            )
        
        # Verify asset state allows transfer
        if self.activo.estado == 'EN_TRANSITO':
            raise ValidationError(
                f"Asset {self.activo.codigo_actual} is already in transit"
            )
        
        # Verify warehouses are still active
        if not self.almacen_origen.activo:
            raise ValidationError(f"Origin warehouse {self.almacen_origen.prefijo} is inactive")
        
        if not self.almacen_destino.activo:
            raise ValidationError(f"Destination warehouse {self.almacen_destino.prefijo} is inactive")
    
    def _execute_asset_code_evolution(self):
        """Execute asset code evolution with validation"""
        old_code = self.activo.codigo_actual
        
        # Evolve asset code
        old_code_returned, new_code = self.activo.evolve_asset_code(self.almacen_destino)
        
        # Validate code evolution
        if old_code != old_code_returned:
            raise ValidationError(
                f"Asset code evolution inconsistency: expected {old_code}, got {old_code_returned}"
            )
        
        # Validate new code format and uniqueness
        if not ActivoInventario.validate_code_uniqueness(new_code, exclude_id=self.activo.id):
            raise ValidationError(f"Evolved asset code {new_code} is not unique")
        
        return old_code, new_code
    
    def _execute_asset_location_update(self):
        """Update asset location atomically"""
        # Update asset location (code already updated in evolution step)
        self.activo.almacen_actual = self.almacen_destino
        self.activo.save()
    
    def _execute_inventory_synchronization(self, executor):
        """Synchronize inventory counts with warehouse systems"""
        from .services import InventorySynchronizationService
        
        try:
            # Synchronize with existing inventory system
            sync_result = InventorySynchronizationService.synchronize_transfer_execution(
                solicitud_traslado=self,
                executor=executor
            )
            
            if not sync_result.success:
                raise ValidationError(
                    f"Inventory synchronization failed: {sync_result.message}"
                )
            
            return sync_result
                
        except Exception as e:
            raise ValidationError(f"Failed to synchronize inventory: {str(e)}")
    
    def _create_transfer_execution_audit_record(self, executor, old_code, new_code):
        """Create comprehensive audit record for transfer execution"""
        from django.utils import timezone
        
        HistorialMovimientoActivo.create_movement_record(
            activo=self.activo,
            tipo_movimiento='TRASLADO_EJECUTADO',
            usuario_responsable=executor,
            motivo=f'Ejecución de traslado: {self.motivo}',
            almacen_origen=self.almacen_origen,
            almacen_destino=self.almacen_destino,
            estado_anterior='EN_ALMACEN',
            estado_nuevo='EN_TRANSITO',
            observaciones=f'Solicitud: {self.numero_solicitud}. Código: {old_code} -> {new_code}',
            solicitud_traslado=self,
            metadata={
                'codigo_anterior': old_code,
                'codigo_nuevo': new_code,
                'fecha_ejecucion': timezone.now().isoformat(),
                'tipo_operacion': 'EJECUCION_TRASLADO'
            }
        )
    
    def _update_execution_status(self, executor):
        """Update request execution status and metadata"""
        from django.utils import timezone
        
        self.estado = 'EN_TRANSITO'
        self.fecha_ejecucion = timezone.now()
        self.ejecutado_por = executor
        self.save()
    
    def _validate_post_execution_state(self):
        """Validate state after execution"""
        # Verify asset is now in destination warehouse
        if self.activo.almacen_actual != self.almacen_destino:
            raise ValidationError(
                f"Post-execution validation failed: asset not in destination warehouse"
            )
        
        # Verify asset state is EN_TRANSITO
        if self.activo.estado != 'EN_TRANSITO':
            raise ValidationError(
                f"Post-execution validation failed: asset state is {self.activo.estado}, expected EN_TRANSITO"
            )
        
        # Verify request state is EN_TRANSITO
        if self.estado != 'EN_TRANSITO':
            raise ValidationError(
                f"Post-execution validation failed: request state is {self.estado}, expected EN_TRANSITO"
            )
    
    @transaction.atomic
    def _rollback_transfer_execution(self, rollback_data, executor):
        """
        Rollback transfer execution to previous state.
        
        This method provides comprehensive rollback capability for failed transfers
        by restoring all modified state to the snapshot taken before execution.
        """
        import logging
        from django.utils import timezone
        
        logger = logging.getLogger(__name__)
        
        try:
            # Restore asset state
            self.activo.codigo_actual = rollback_data['activo_codigo_actual']
            self.activo.almacen_actual_id = rollback_data['activo_almacen_actual']
            self.activo.estado = rollback_data['activo_estado']
            self.activo.save()
            
            # Restore request state
            self.estado = rollback_data['solicitud_estado']
            self.fecha_ejecucion = rollback_data['solicitud_fecha_ejecucion']
            self.ejecutado_por_id = rollback_data['solicitud_ejecutado_por']
            self.save()
            
            # Create rollback audit record
            HistorialMovimientoActivo.create_movement_record(
                activo=self.activo,
                tipo_movimiento='ROLLBACK_TRASLADO',
                usuario_responsable=executor,
                motivo=f'Rollback de ejecución fallida: {self.numero_solicitud}',
                almacen_origen=self.almacen_destino,  # Reversed for rollback
                almacen_destino=self.almacen_origen,  # Reversed for rollback
                estado_anterior='EN_TRANSITO',
                estado_nuevo=rollback_data['activo_estado'],
                observaciones=f'Rollback automático por falla en ejecución',
                solicitud_traslado=self,
                metadata={
                    'tipo_operacion': 'ROLLBACK_EJECUCION',
                    'rollback_timestamp': timezone.now().isoformat(),
                    'original_snapshot': rollback_data
                }
            )
            
            logger.info(f"Transfer execution rollback completed for {self.numero_solicitud}")
            
        except Exception as e:
            logger.error(f"Failed to rollback transfer execution: {str(e)}")
            raise
    
    def complete_transfer(self, receiver):
        """Complete the transfer when asset arrives at destination with state management"""
        if self.estado != 'EN_TRANSITO':
            raise ValidationError('Solo se pueden completar traslados en tránsito')
        
        from django.utils import timezone
        from .state_management import AssetStateManager
        
        # Handle state change using state management system
        AssetStateManager.handle_transfer_state_changes(
            solicitud_traslado=self,
            stage='completed',
            user=receiver
        )
        
        # Create completion record
        HistorialMovimientoActivo.create_movement_record(
            activo=self.activo,
            tipo_movimiento='TRASLADO_ALMACEN',
            usuario_responsable=receiver,
            motivo=f'Recepción de traslado {self.numero_solicitud}',
            almacen_origen=self.almacen_origen,
            almacen_destino=self.almacen_destino,
            estado_anterior='EN_TRANSITO',
            estado_nuevo='EN_ALMACEN',
            observaciones=f'Completado: {self.numero_solicitud}',
            solicitud_traslado=self
        )
        
        # Update request status
        self.estado = 'COMPLETADA'
        self.fecha_completada = timezone.now()
        self.save()


class AprobacionTraslado(models.Model):
    """
    Individual approval record in dual approval workflow.
    Tracks approval decisions from warehouse managers.
    """
    
    APPROVAL_TYPES = [
        ('ORIGEN', 'Origen'),
        ('DESTINO', 'Destino'),
    ]
    
    DECISIONS = [
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]
    
    # Request reference
    solicitud = models.ForeignKey(
        SolicitudTraslado,
        on_delete=models.CASCADE,
        related_name='aprobaciones',
        help_text='Solicitud de traslado'
    )
    
    # Approval details
    aprobador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='aprobaciones_realizadas',
        help_text='Usuario que realizó la aprobación'
    )
    tipo_aprobacion = models.CharField(
        max_length=10,
        choices=APPROVAL_TYPES,
        help_text='Tipo de aprobación (origen o destino)'
    )
    decision = models.CharField(
        max_length=10,
        choices=DECISIONS,
        help_text='Decisión tomada'
    )
    fecha_decision = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de la decisión'
    )
    comentarios = models.TextField(
        blank=True,
        help_text='Comentarios sobre la decisión'
    )
    
    class Meta:
        verbose_name = 'Aprobación de Traslado'
        verbose_name_plural = 'Aprobaciones de Traslado'
        unique_together = ['solicitud', 'tipo_aprobacion']
        ordering = ['-fecha_decision']
        indexes = [
            models.Index(fields=['aprobador', '-fecha_decision']),
            models.Index(fields=['decision', '-fecha_decision']),
            models.Index(fields=['solicitud', 'tipo_aprobacion']),
            # Additional indexes for manager dashboard queries
            models.Index(fields=['aprobador', 'decision', '-fecha_decision']),
            models.Index(fields=['tipo_aprobacion', 'decision', '-fecha_decision']),
            models.Index(fields=['solicitud', 'decision']),
        ]
    
    def __str__(self):
        return f"{self.solicitud.numero_solicitud} - {self.get_tipo_aprobacion_display()} - {self.get_decision_display()}"
    
    def clean(self):
        """Custom validation for approval records"""
        from django.core.exceptions import ValidationError
        
        # Validate that approver is the correct warehouse manager
        if self.tipo_aprobacion == 'ORIGEN':
            if self.aprobador != self.solicitud.almacen_origen.manager:
                raise ValidationError(
                    'Solo el gerente del almacén origen puede aprobar desde origen'
                )
        elif self.tipo_aprobacion == 'DESTINO':
            if self.aprobador != self.solicitud.almacen_destino.manager:
                raise ValidationError(
                    'Solo el gerente del almacén destino puede aprobar desde destino'
                )
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation and update workflow state"""
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Update the related solicitud's workflow state and approval references
        self.update_solicitud_workflow_state()
    
    def update_solicitud_workflow_state(self):
        """Update the related solicitud's workflow state and approval references"""
        solicitud = self.solicitud
        
        # Update approval references in solicitud
        if self.tipo_aprobacion == 'ORIGEN':
            solicitud.aprobacion_origen = self
        elif self.tipo_aprobacion == 'DESTINO':
            solicitud.aprobacion_destino = self
        
        # Update workflow state
        solicitud.update_workflow_state()
        
        # Handle automatic state changes for asset ONLY if both approvals are complete
        # and this is the final approval that completes the dual approval
        if (solicitud.estado == 'APROBADA_COMPLETA' and 
            solicitud.aprobacion_origen and solicitud.aprobacion_destino and
            solicitud.aprobacion_origen.decision == 'APROBADO' and
            solicitud.aprobacion_destino.decision == 'APROBADO'):
            
            from .state_management import AssetStateManager
            
            # Only change state if asset is still in warehouse (not already in transit)
            if solicitud.activo.estado == 'EN_ALMACEN':
                AssetStateManager.handle_transfer_state_changes(
                    solicitud_traslado=solicitud,
                    stage='approved',
                    user=self.aprobador
                )
                
                # Update solicitud state to EN_TRANSITO when asset state changes
                if solicitud.activo.estado == 'EN_TRANSITO':
                    from django.utils import timezone
                    solicitud.estado = 'EN_TRANSITO'
                    solicitud.fecha_ejecucion = timezone.now()
                    solicitud.ejecutado_por = self.aprobador
                    solicitud.save()
    
    def can_be_modified(self):
        """Check if this approval can be modified"""
        # Approvals cannot be modified once the transfer is executed or completed
        return self.solicitud.estado not in ['EN_TRANSITO', 'COMPLETADA']
    
    def get_approval_summary(self):
        """Get human-readable approval summary"""
        warehouse = (self.solicitud.almacen_origen if self.tipo_aprobacion == 'ORIGEN' 
                    else self.solicitud.almacen_destino)
        
        return {
            'warehouse': warehouse,
            'warehouse_name': warehouse.nombre,
            'warehouse_prefix': warehouse.prefijo,
            'approver': self.aprobador,
            'decision': self.get_decision_display(),
            'date': self.fecha_decision,
            'comments': self.comentarios,
            'can_modify': self.can_be_modified()
        }
    
    @classmethod
    def create_approval(cls, solicitud, aprobador, tipo_aprobacion, decision, comentarios=''):
        """Create a new approval with validation"""
        from django.core.exceptions import ValidationError
        
        # Validate that approver is authorized
        if tipo_aprobacion == 'ORIGEN':
            if aprobador != solicitud.almacen_origen.manager:
                raise ValidationError('Solo el gerente del almacén origen puede aprobar desde origen')
        elif tipo_aprobacion == 'DESTINO':
            if aprobador != solicitud.almacen_destino.manager:
                raise ValidationError('Solo el gerente del almacén destino puede aprobar desde destino')
        
        # Check if approval already exists
        existing = cls.objects.filter(
            solicitud=solicitud,
            tipo_aprobacion=tipo_aprobacion
        ).first()
        
        if existing and not existing.can_be_modified():
            raise ValidationError('Esta aprobación ya no puede ser modificada')
        
        # Create or update approval
        if existing:
            existing.decision = decision
            existing.comentarios = comentarios
            existing.save()
            return existing
        else:
            return cls.objects.create(
                solicitud=solicitud,
                aprobador=aprobador,
                tipo_aprobacion=tipo_aprobacion,
                decision=decision,
                comentarios=comentarios
            )
    
    @classmethod
    def get_pending_for_user(cls, user):
        """Get pending approvals for a specific user"""
        from django.db.models import Q
        
        # Find solicitudes where this user is a manager and approval is pending
        pending_solicitudes = []
        
        # Check for origin approvals
        origin_pending = SolicitudTraslado.objects.filter(
            almacen_origen__manager=user,
            aprobacion_origen__isnull=True,
            estado__in=['PENDIENTE', 'APROBADA_DESTINO']
        )
        
        for solicitud in origin_pending:
            pending_solicitudes.append({
                'solicitud': solicitud,
                'tipo_aprobacion': 'ORIGEN',
                'warehouse': solicitud.almacen_origen
            })
        
        # Check for destination approvals
        destino_pending = SolicitudTraslado.objects.filter(
            almacen_destino__manager=user,
            aprobacion_destino__isnull=True,
            estado__in=['PENDIENTE', 'APROBADA_ORIGEN']
        )
        
        for solicitud in destino_pending:
            pending_solicitudes.append({
                'solicitud': solicitud,
                'tipo_aprobacion': 'DESTINO',
                'warehouse': solicitud.almacen_destino
            })
        
        return pending_solicitudes
    
    @classmethod
    def get_approval_history_for_user(cls, user, limit=20):
        """Get approval history for a specific user"""
        return cls.objects.filter(
            aprobador=user
        ).select_related(
            'solicitud__activo',
            'solicitud__almacen_origen',
            'solicitud__almacen_destino'
        ).order_by('-fecha_decision')[:limit]
    
    @classmethod
    def get_approval_statistics(cls, user=None, warehouse=None):
        """Get approval statistics"""
        from django.db.models import Count, Q
        from django.utils import timezone
        
        queryset = cls.objects.all()
        
        if user:
            queryset = queryset.filter(aprobador=user)
        
        if warehouse:
            queryset = queryset.filter(
                Q(solicitud__almacen_origen=warehouse, tipo_aprobacion='ORIGEN') |
                Q(solicitud__almacen_destino=warehouse, tipo_aprobacion='DESTINO')
            )
        
        # Count by decision
        decision_counts = queryset.values('decision').annotate(
            count=Count('id')
        )
        
        # Recent activity (last 30 days)
        month_ago = timezone.now() - timezone.timedelta(days=30)
        recent_approvals = queryset.filter(fecha_decision__gte=month_ago).count()
        
        # Average response time (this would need additional tracking)
        total_approvals = queryset.count()
        
        decision_breakdown = {item['decision']: item['count'] for item in decision_counts}
        approved_count = decision_breakdown.get('APROBADO', 0)
        
        return {
            'total_approvals': total_approvals,
            'recent_approvals': recent_approvals,
            'decision_breakdown': decision_breakdown,
            'approval_rate': (approved_count / total_approvals * 100 if total_approvals > 0 else 0)
        }


class AcueductoNuevo(models.Model):
    """
    New Acueducto model for the hierarchical structure.
    This model represents water systems under the new organizational hierarchy.
    """
    TIPO_SISTEMA_CHOICES = [
        ('ACUEDUCTO', 'Acueducto'),
        ('PLANTA_TRATAMIENTO', 'Planta de Tratamiento'),
        ('SISTEMA_BOMBEO', 'Sistema de Bombeo'),
        ('EMBALSE', 'Embalse'),
        ('POZO', 'Pozo'),
    ]
    
    unidad_organizacional = models.ForeignKey(
        UnidadOrganizacional,
        on_delete=models.CASCADE,
        related_name='acueductos_nuevos',
        help_text='Unidad organizacional responsable'
    )
    tipo_sistema = models.CharField(
        max_length=20,
        choices=TIPO_SISTEMA_CHOICES,
        default='ACUEDUCTO',
        help_text='Tipo de sistema de agua'
    )
    nombre = models.CharField(
        max_length=200,
        help_text='Nombre del acueducto o sistema'
    )
    codigo = models.CharField(
        max_length=20,
        help_text='Código identificador único'
    )
    responsable_operativo = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='acueductos_operados',
        help_text='Responsable operativo del acueducto'
    )
    ubicacion = models.CharField(
        max_length=255,
        blank=True,
        help_text='Ubicación geográfica'
    )
    capacidad_produccion = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Capacidad de producción (litros/segundo)'
    )
    poblacion_servida = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Población aproximada servida'
    )
    fecha_inauguracion = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    # Audit fields
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='acueductos_nuevos_creados',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Acueducto Nuevo'
        verbose_name_plural = 'Acueductos Nuevos'
        unique_together = [
            ('unidad_organizacional', 'codigo')
        ]
        ordering = ['unidad_organizacional', 'nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
            models.Index(fields=['tipo_sistema']),
            models.Index(fields=['unidad_organizacional']),
        ]
    
    def __str__(self):
        return f"{self.nombre} - {self.unidad_organizacional.codigo}"
    
    def clean(self):
        """Custom validation for AcueductoNuevo"""
        from django.core.exceptions import ValidationError
        
        # Ensure unique codigo within unidad_organizacional
        if self.codigo and self.unidad_organizacional:
            existing = AcueductoNuevo.objects.filter(
                unidad_organizacional=self.unidad_organizacional,
                codigo=self.codigo
            ).exclude(pk=self.pk)
            
            if existing.exists():
                raise ValidationError({
                    'codigo': f'Ya existe un acueducto con código "{self.codigo}" en esta unidad organizacional'
                })
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def vicepresidencia(self):
        """Get the vicepresidencia this acueducto belongs to"""
        return self.unidad_organizacional.vicepresidencia
    
    @property
    def empresa(self):
        """Get the empresa this acueducto belongs to"""
        return self.unidad_organizacional.vicepresidencia.empresa
    
    @property
    def ruta_organizacional_completa(self):
        """Get complete organizational path"""
        return f"{self.empresa.nombre} → {self.vicepresidencia.nombre} → {self.unidad_organizacional.nombre} → {self.nombre}"
    
    def get_full_path(self):
        """Return full hierarchical path including acueducto"""
        base_path = self.unidad_organizacional.get_full_path()
        return f"{base_path} → {self.nombre}"

# ============================================================================
# COMPREHENSIVE AUDIT TRAIL MODELS
# ============================================================================

class AuditTrailBase(models.Model):
    """
    Base class for all audit trail models.
    Provides common fields and immutability enforcement.
    
    Requirements implemented:
    - 6.1: Immutable movement records for complete asset traceability
    - 6.2: Audit models for state changes and approval decisions
    - 6.4: Proper indexing for audit queries and reporting
    - 6.5: Comprehensive audit trail system
    
    This abstract base class ensures all audit models have consistent
    structure, proper indexing, and immutability enforcement.
    """
    
    # Audit metadata with enhanced tracking
    fecha_auditoria = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when audit record was created (immutable)',
        db_index=True  # Index for performance
    )
    usuario_responsable = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_audit_records',
        help_text='User responsible for the audited action',
        db_index=True  # Index for user-based queries
    )
    
    # Enhanced tracking fields
    direccion_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address from which the action was performed',
        db_index=True  # Index for security analysis
    )
    user_agent = models.TextField(
        blank=True,
        help_text='User agent string from the request'
    )
    session_key = models.CharField(
        max_length=40,
        blank=True,
        help_text='Session key for tracking user sessions',
        db_index=True  # Index for session analysis
    )
    
    # Request context for web-based actions
    request_method = models.CharField(
        max_length=10,
        blank=True,
        help_text='HTTP method used for the request'
    )
    request_path = models.CharField(
        max_length=500,
        blank=True,
        help_text='Request path/URL'
    )
    
    # Additional context with enhanced structure
    contexto_adicional = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional context information for the audit record'
    )
    
    # Audit integrity fields
    checksum = models.CharField(
        max_length=64,
        blank=True,
        help_text='SHA-256 checksum for audit record integrity verification'
    )
    
    class Meta:
        abstract = True
        ordering = ['-fecha_auditoria']
        indexes = [
            # Base indexes that all audit models will inherit
            models.Index(fields=['-fecha_auditoria'], name='%(class)s_fecha_idx'),
            models.Index(fields=['usuario_responsable', '-fecha_auditoria'], name='%(class)s_usr_fecha_idx'),
            models.Index(fields=['direccion_ip', '-fecha_auditoria'], name='%(class)s_ip_fecha_idx'),
            models.Index(fields=['session_key', '-fecha_auditoria'], name='%(class)s_sess_fecha_idx'),
        ]
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure immutability and generate integrity checksum.
        
        Implements requirement 6.1: Immutable movement records for complete asset traceability
        """
        if self.pk:
            raise ValidationError(
                'Los registros de auditoría son inmutables y no pueden ser modificados después de su creación. '
                'Esta restricción garantiza la integridad del audit trail.'
            )
        
        # Generate integrity checksum before saving
        self._generate_checksum()
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """
        Override delete to prevent deletion of audit records.
        
        Implements requirement 6.5: Comprehensive audit trail system
        """
        raise ValidationError(
            'Los registros de auditoría no pueden ser eliminados. '
            'La inmutabilidad de los registros de auditoría es fundamental para la integridad del sistema.'
        )
    
    def _generate_checksum(self):
        """Generate SHA-256 checksum for audit record integrity"""
        import hashlib
        import json
        from django.utils import timezone
        
        # Create a consistent representation of the record for checksumming
        checksum_data = {
            'fecha_auditoria': self.fecha_auditoria.isoformat() if self.fecha_auditoria else timezone.now().isoformat(),
            'usuario_responsable_id': self.usuario_responsable_id,
            'direccion_ip': self.direccion_ip or '',
            'user_agent': self.user_agent or '',
            'session_key': self.session_key or '',
            'request_method': getattr(self, 'request_method', '') or '',
            'request_path': getattr(self, 'request_path', '') or '',
            'contexto_adicional': self.contexto_adicional or {},
        }
        
        # Add model-specific fields for checksum
        checksum_data.update(self._get_checksum_fields())
        
        # Generate checksum
        checksum_string = json.dumps(checksum_data, sort_keys=True, default=str)
        self.checksum = hashlib.sha256(checksum_string.encode()).hexdigest()
    
    def _get_checksum_fields(self):
        """Override in subclasses to include model-specific fields in checksum"""
        return {}
    
    def verify_integrity(self):
        """
        Verify the integrity of this audit record by recalculating checksum.
        
        Returns:
            bool: True if integrity is verified, False otherwise
        """
        if not self.checksum:
            return False
        
        original_checksum = self.checksum
        self._generate_checksum()
        current_checksum = self.checksum
        
        # Restore original checksum
        self.checksum = original_checksum
        
        return original_checksum == current_checksum
    
    @classmethod
    def verify_audit_trail_integrity(cls, start_date=None, end_date=None):
        """
        Verify integrity of multiple audit records.
        
        Args:
            start_date: Start date for verification range
            end_date: End date for verification range
            
        Returns:
            dict: Verification results with statistics
        """
        queryset = cls.objects.all()
        
        if start_date:
            queryset = queryset.filter(fecha_auditoria__gte=start_date)
        if end_date:
            queryset = queryset.filter(fecha_auditoria__lte=end_date)
        
        total_records = queryset.count()
        verified_records = 0
        failed_records = []
        
        for record in queryset:
            if record.verify_integrity():
                verified_records += 1
            else:
                failed_records.append({
                    'id': record.id,
                    'fecha_auditoria': record.fecha_auditoria,
                    'usuario_responsable': record.usuario_responsable.username if record.usuario_responsable else None
                })
        
        return {
            'total_records': total_records,
            'verified_records': verified_records,
            'failed_records': len(failed_records),
            'integrity_percentage': (verified_records / total_records * 100) if total_records > 0 else 0,
            'failed_record_details': failed_records
        }


class AuditoriaEstadoActivo(AuditTrailBase):
    """
    Audit trail for asset state changes.
    Records all state transitions with complete context.
    """
    
    AUDIT_ACTIONS = [
        ('STATE_CHANGE', 'Cambio de Estado'),
        ('STATE_CHANGE_AUTO', 'Cambio de Estado Automático'),
        ('STATE_VALIDATION', 'Validación de Estado'),
        ('STATE_CORRECTION', 'Corrección de Estado'),
    ]
    
    # Asset reference
    activo = models.ForeignKey(
        ActivoInventario,
        on_delete=models.CASCADE,
        related_name='auditoria_estados',
        help_text='Activo cuyo estado fue modificado'
    )
    
    # State change details
    accion = models.CharField(
        max_length=20,
        choices=AUDIT_ACTIONS,
        help_text='Tipo de acción realizada'
    )
    estado_anterior = models.CharField(
        max_length=20,
        choices=ActivoInventario.ASSET_STATES,
        help_text='Estado anterior del activo'
    )
    estado_nuevo = models.CharField(
        max_length=20,
        choices=ActivoInventario.ASSET_STATES,
        help_text='Estado nuevo del activo'
    )
    
    # Change context
    motivo = models.TextField(
        help_text='Motivo del cambio de estado'
    )
    observaciones = models.TextField(
        blank=True,
        help_text='Observaciones adicionales sobre el cambio'
    )
    
    # Validation results
    validacion_exitosa = models.BooleanField(
        default=True,
        help_text='Indica si la validación del cambio fue exitosa'
    )
    errores_validacion = models.JSONField(
        default=list,
        blank=True,
        help_text='Lista de errores de validación si los hubo'
    )
    
    # Related records
    solicitud_traslado = models.ForeignKey(
        SolicitudTraslado,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='auditoria_estados',
        help_text='Solicitud de traslado relacionada (si aplica)'
    )
    
    class Meta:
        verbose_name = 'Auditoría de Estado de Activo'
        verbose_name_plural = 'Auditorías de Estados de Activos'
        ordering = ['-fecha_auditoria']
        indexes = [
            # Primary audit indexes
            models.Index(fields=['activo', '-fecha_auditoria'], name='idx_aud_est_activo_fecha'),
            models.Index(fields=['accion', '-fecha_auditoria'], name='idx_aud_est_accion_fecha'),
            models.Index(fields=['usuario_responsable', '-fecha_auditoria'], name='idx_aud_est_usuario_fecha'),
            
            # State transition indexes for reporting
            models.Index(fields=['estado_anterior', 'estado_nuevo'], name='idx_aud_est_transicion'),
            models.Index(fields=['estado_anterior', 'estado_nuevo', '-fecha_auditoria'], name='idx_aud_est_trans_fecha'),
            models.Index(fields=['validacion_exitosa', '-fecha_auditoria'], name='idx_aud_est_valid_fecha'),
            
            # Complex query indexes
            models.Index(fields=['activo', 'accion', '-fecha_auditoria'], name='idx_aud_est_act_acc_fecha'),
            models.Index(fields=['activo', 'estado_nuevo', '-fecha_auditoria'], name='idx_aud_est_act_new_fecha'),
            models.Index(fields=['solicitud_traslado', '-fecha_auditoria'], name='idx_aud_est_sol_fecha'),
            
            # Performance indexes for dashboard queries
            models.Index(fields=['accion', 'validacion_exitosa', '-fecha_auditoria'], name='idx_aud_est_acc_val_fecha'),
            models.Index(fields=['usuario_responsable', 'accion', '-fecha_auditoria'], name='idx_aud_est_usr_acc_fecha'),
        ]
        constraints = [
            # Ensure state transitions are logical
            models.CheckConstraint(
                check=~models.Q(estado_anterior=models.F('estado_nuevo')),
                name='audit_estado_different_states'
            ),
        ]
    
    def __str__(self):
        return f"{self.activo.codigo_actual} - {self.estado_anterior} → {self.estado_nuevo} - {self.fecha_auditoria.strftime('%Y-%m-%d %H:%M')}"
    
    def get_change_summary(self):
        """Get a human-readable summary of the state change"""
        return f"{self.get_accion_display()}: {self.estado_anterior} → {self.estado_nuevo}"
    
    @classmethod
    def create_state_change_audit(cls, activo, old_state, new_state, user, motivo, 
                                 observaciones='', solicitud_traslado=None, 
                                 ip_address=None, user_agent='', session_key='',
                                 contexto_adicional=None):
        """Create a state change audit record"""
        if contexto_adicional is None:
            contexto_adicional = {}
        
        return cls.objects.create(
            activo=activo,
            accion='STATE_CHANGE',
            estado_anterior=old_state,
            estado_nuevo=new_state,
            usuario_responsable=user,
            motivo=motivo,
            observaciones=observaciones,
            solicitud_traslado=solicitud_traslado,
            direccion_ip=ip_address,
            user_agent=user_agent,
            session_key=session_key,
            contexto_adicional=contexto_adicional
        )
    
    def _get_checksum_fields(self):
        """Include model-specific fields in checksum calculation"""
        return {
            'activo_id': self.activo_id,
            'accion': self.accion,
            'estado_anterior': self.estado_anterior,
            'estado_nuevo': self.estado_nuevo,
            'motivo': self.motivo,
            'observaciones': self.observaciones,
            'validacion_exitosa': self.validacion_exitosa,
            'errores_validacion': self.errores_validacion,
            'solicitud_traslado_id': self.solicitud_traslado_id if self.solicitud_traslado else None,
        }
    
    @classmethod
    def get_state_transition_report(cls, activo=None, start_date=None, end_date=None):
        """
        Generate state transition report for compliance and analysis.
        
        Args:
            activo: Specific asset to report on (optional)
            start_date: Start date for report range
            end_date: End date for report range
            
        Returns:
            dict: Comprehensive state transition report
        """
        from django.db.models import Count, Q
        from django.utils import timezone
        
        queryset = cls.objects.all()
        
        if activo:
            queryset = queryset.filter(activo=activo)
        if start_date:
            queryset = queryset.filter(fecha_auditoria__gte=start_date)
        if end_date:
            queryset = queryset.filter(fecha_auditoria__lte=end_date)
        
        # State transition statistics
        transitions = queryset.values('estado_anterior', 'estado_nuevo').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Validation statistics
        validation_stats = queryset.aggregate(
            total_changes=Count('id'),
            successful_validations=Count('id', filter=Q(validacion_exitosa=True)),
            failed_validations=Count('id', filter=Q(validacion_exitosa=False))
        )
        
        # User activity statistics
        user_stats = queryset.values('usuario_responsable__username').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'asset': activo.codigo_actual if activo else 'All Assets'
            },
            'summary': {
                'total_state_changes': validation_stats['total_changes'],
                'successful_validations': validation_stats['successful_validations'],
                'failed_validations': validation_stats['failed_validations'],
                'validation_success_rate': (
                    validation_stats['successful_validations'] / validation_stats['total_changes'] * 100
                    if validation_stats['total_changes'] > 0 else 0
                )
            },
            'state_transitions': list(transitions),
            'top_users': list(user_stats),
            'generated_at': timezone.now().isoformat()
        }


class AuditoriaAprobacion(AuditTrailBase):
    """
    Audit trail for approval and rejection decisions.
    Records all approval workflow actions with complete context.
    """
    
    AUDIT_ACTIONS = [
        ('APPROVAL_GRANTED', 'Aprobación Otorgada'),
        ('APPROVAL_REJECTED', 'Aprobación Rechazada'),
        ('APPROVAL_REVOKED', 'Aprobación Revocada'),
        ('APPROVAL_DELEGATED', 'Aprobación Delegada'),
        ('APPROVAL_ESCALATED', 'Aprobación Escalada'),
    ]
    
    # Approval reference
    solicitud_traslado = models.ForeignKey(
        SolicitudTraslado,
        on_delete=models.CASCADE,
        related_name='auditoria_aprobaciones',
        help_text='Solicitud de traslado relacionada'
    )
    aprobacion = models.ForeignKey(
        AprobacionTraslado,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='auditoria_records',
        help_text='Registro de aprobación relacionado'
    )
    
    # Approval details
    accion = models.CharField(
        max_length=20,
        choices=AUDIT_ACTIONS,
        help_text='Tipo de acción de aprobación realizada'
    )
    tipo_aprobacion = models.CharField(
        max_length=10,
        choices=AprobacionTraslado.APPROVAL_TYPES,
        help_text='Tipo de aprobación (origen o destino)'
    )
    decision = models.CharField(
        max_length=10,
        choices=AprobacionTraslado.DECISIONS,
        help_text='Decisión tomada'
    )
    
    # Decision context
    comentarios = models.TextField(
        blank=True,
        help_text='Comentarios sobre la decisión'
    )
    motivo_rechazo = models.TextField(
        blank=True,
        help_text='Motivo detallado del rechazo (si aplica)'
    )
    
    # Approval authority validation
    autoridad_validada = models.BooleanField(
        default=True,
        help_text='Indica si la autoridad del aprobador fue validada'
    )
    errores_autoridad = models.JSONField(
        default=list,
        blank=True,
        help_text='Lista de errores de validación de autoridad'
    )
    
    # Workflow impact
    estado_solicitud_anterior = models.CharField(
        max_length=20,
        choices=SolicitudTraslado.TRANSFER_STATES,
        help_text='Estado anterior de la solicitud'
    )
    estado_solicitud_nuevo = models.CharField(
        max_length=20,
        choices=SolicitudTraslado.TRANSFER_STATES,
        help_text='Estado nuevo de la solicitud'
    )
    
    class Meta:
        verbose_name = 'Auditoría de Aprobación'
        verbose_name_plural = 'Auditorías de Aprobaciones'
        ordering = ['-fecha_auditoria']
        indexes = [
            # Primary audit indexes
            models.Index(fields=['solicitud_traslado', '-fecha_auditoria'], name='idx_aud_apr_sol_fecha'),
            models.Index(fields=['accion', '-fecha_auditoria'], name='idx_aud_apr_accion_fecha'),
            models.Index(fields=['usuario_responsable', '-fecha_auditoria'], name='idx_aud_apr_usuario_fecha'),
            
            # Approval workflow indexes
            models.Index(fields=['decision', '-fecha_auditoria'], name='idx_aud_apr_decision_fecha'),
            models.Index(fields=['tipo_aprobacion', 'decision'], name='idx_aud_apr_tipo_decision'),
            models.Index(fields=['tipo_aprobacion', 'decision', '-fecha_auditoria'], name='idx_aud_apr_tip_dec_fecha'),
            models.Index(fields=['autoridad_validada', '-fecha_auditoria'], name='idx_aud_apr_autor_fecha'),
            
            # Workflow state tracking indexes
            models.Index(fields=['estado_solicitud_anterior', 'estado_solicitud_nuevo'], name='idx_aud_apr_estados'),
            models.Index(fields=['estado_solicitud_nuevo', '-fecha_auditoria'], name='idx_aud_apr_est_new_fecha'),
            
            # Complex query indexes for reporting
            models.Index(fields=['accion', 'autoridad_validada', '-fecha_auditoria'], name='idx_aud_apr_acc_aut_fecha'),
            models.Index(fields=['usuario_responsable', 'decision', '-fecha_auditoria'], name='idx_aud_apr_usr_dec_fecha'),
            models.Index(fields=['solicitud_traslado', 'tipo_aprobacion', '-fecha_auditoria'], name='idx_aud_apr_sol_tip_fecha'),
            
            # Performance indexes for manager dashboards
            models.Index(fields=['aprobacion', '-fecha_auditoria'], name='idx_aud_apr_aprob_fecha'),
            models.Index(fields=['decision', 'autoridad_validada', '-fecha_auditoria'], name='idx_aud_apr_dec_aut_fecha'),
        ]
    
    def __str__(self):
        return f"{self.solicitud_traslado.numero_solicitud} - {self.get_accion_display()} - {self.fecha_auditoria.strftime('%Y-%m-%d %H:%M')}"
    
    def get_decision_summary(self):
        """Get a human-readable summary of the approval decision"""
        return f"{self.get_tipo_aprobacion_display()}: {self.get_decision_display()}"
    
    @classmethod
    def create_approval_audit(cls, solicitud_traslado, aprobacion, accion, user,
                            comentarios='', motivo_rechazo='', ip_address=None,
                            user_agent='', session_key='', contexto_adicional=None):
        """Create an approval audit record"""
        if contexto_adicional is None:
            contexto_adicional = {}
        
        # Get workflow state information
        estado_anterior = solicitud_traslado.estado
        
        return cls.objects.create(
            solicitud_traslado=solicitud_traslado,
            aprobacion=aprobacion,
            accion=accion,
            tipo_aprobacion=aprobacion.tipo_aprobacion if aprobacion else '',
            decision=aprobacion.decision if aprobacion else '',
            usuario_responsable=user,
            comentarios=comentarios,
            motivo_rechazo=motivo_rechazo,
            estado_solicitud_anterior=estado_anterior,
            estado_solicitud_nuevo=solicitud_traslado.estado,
            direccion_ip=ip_address,
            user_agent=user_agent,
            session_key=session_key,
            contexto_adicional=contexto_adicional
        )
    
    def _get_checksum_fields(self):
        """Include model-specific fields in checksum calculation"""
        return {
            'solicitud_traslado_id': self.solicitud_traslado_id,
            'aprobacion_id': self.aprobacion_id if self.aprobacion else None,
            'accion': self.accion,
            'tipo_aprobacion': self.tipo_aprobacion,
            'decision': self.decision,
            'comentarios': self.comentarios,
            'motivo_rechazo': self.motivo_rechazo,
            'autoridad_validada': self.autoridad_validada,
            'errores_autoridad': self.errores_autoridad,
            'estado_solicitud_anterior': self.estado_solicitud_anterior,
            'estado_solicitud_nuevo': self.estado_solicitud_nuevo,
        }
    
    @classmethod
    def get_approval_workflow_report(cls, warehouse=None, manager=None, start_date=None, end_date=None):
        """
        Generate approval workflow report for compliance and performance analysis.
        
        Args:
            warehouse: Specific warehouse to report on (optional)
            manager: Specific manager to report on (optional)
            start_date: Start date for report range
            end_date: End date for report range
            
        Returns:
            dict: Comprehensive approval workflow report
        """
        from django.db.models import Count, Q, Avg
        from django.utils import timezone
        
        queryset = cls.objects.all()
        
        if warehouse:
            queryset = queryset.filter(
                Q(solicitud_traslado__almacen_origen=warehouse) |
                Q(solicitud_traslado__almacen_destino=warehouse)
            )
        if manager:
            queryset = queryset.filter(usuario_responsable=manager)
        if start_date:
            queryset = queryset.filter(fecha_auditoria__gte=start_date)
        if end_date:
            queryset = queryset.filter(fecha_auditoria__lte=end_date)
        
        # Approval statistics
        approval_stats = queryset.aggregate(
            total_approvals=Count('id'),
            granted_approvals=Count('id', filter=Q(decision='APROBADO')),
            rejected_approvals=Count('id', filter=Q(decision='RECHAZADO')),
            origin_approvals=Count('id', filter=Q(tipo_aprobacion='ORIGEN')),
            destination_approvals=Count('id', filter=Q(tipo_aprobacion='DESTINO')),
            authority_validated=Count('id', filter=Q(autoridad_validada=True)),
        )
        
        # Decision breakdown by type
        decision_breakdown = queryset.values('tipo_aprobacion', 'decision').annotate(
            count=Count('id')
        ).order_by('tipo_aprobacion', 'decision')
        
        # Manager performance
        manager_stats = queryset.values('usuario_responsable__username').annotate(
            total_decisions=Count('id'),
            approvals=Count('id', filter=Q(decision='APROBADO')),
            rejections=Count('id', filter=Q(decision='RECHAZADO'))
        ).order_by('-total_decisions')[:10]
        
        return {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'warehouse': warehouse.nombre if warehouse else 'All Warehouses',
                'manager': manager.username if manager else 'All Managers'
            },
            'summary': {
                'total_approvals': approval_stats['total_approvals'],
                'granted_approvals': approval_stats['granted_approvals'],
                'rejected_approvals': approval_stats['rejected_approvals'],
                'approval_rate': (
                    approval_stats['granted_approvals'] / approval_stats['total_approvals'] * 100
                    if approval_stats['total_approvals'] > 0 else 0
                ),
                'origin_approvals': approval_stats['origin_approvals'],
                'destination_approvals': approval_stats['destination_approvals'],
                'authority_validation_rate': (
                    approval_stats['authority_validated'] / approval_stats['total_approvals'] * 100
                    if approval_stats['total_approvals'] > 0 else 0
                )
            },
            'decision_breakdown': list(decision_breakdown),
            'manager_performance': list(manager_stats),
            'generated_at': timezone.now().isoformat()
        }


class AuditoriaOperacionSistema(AuditTrailBase):
    """
    Audit trail for system operations and administrative actions.
    Records system-level operations that affect multiple entities.
    """
    
    AUDIT_ACTIONS = [
        ('SYSTEM_MIGRATION', 'Migración del Sistema'),
        ('DATA_IMPORT', 'Importación de Datos'),
        ('DATA_EXPORT', 'Exportación de Datos'),
        ('BULK_UPDATE', 'Actualización Masiva'),
        ('SYSTEM_MAINTENANCE', 'Mantenimiento del Sistema'),
        ('CONFIGURATION_CHANGE', 'Cambio de Configuración'),
        ('PERMISSION_CHANGE', 'Cambio de Permisos'),
        ('USER_MANAGEMENT', 'Gestión de Usuarios'),
        ('WAREHOUSE_MANAGEMENT', 'Gestión de Almacenes'),
        ('INVENTORY_RECONCILIATION', 'Reconciliación de Inventario'),
    ]
    
    # Operation details
    accion = models.CharField(
        max_length=30,
        choices=AUDIT_ACTIONS,
        help_text='Tipo de operación del sistema realizada'
    )
    descripcion = models.TextField(
        help_text='Descripción detallada de la operación'
    )
    
    # Operation scope
    entidades_afectadas = models.JSONField(
        default=list,
        help_text='Lista de entidades afectadas por la operación'
    )
    parametros_operacion = models.JSONField(
        default=dict,
        help_text='Parámetros utilizados en la operación'
    )
    
    # Operation results
    exitosa = models.BooleanField(
        default=True,
        help_text='Indica si la operación fue exitosa'
    )
    errores = models.JSONField(
        default=list,
        blank=True,
        help_text='Lista de errores ocurridos durante la operación'
    )
    warnings = models.JSONField(
        default=list,
        blank=True,
        help_text='Lista de advertencias generadas durante la operación'
    )
    
    # Performance metrics
    duracion_segundos = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        help_text='Duración de la operación en segundos'
    )
    registros_procesados = models.IntegerField(
        null=True,
        blank=True,
        help_text='Número de registros procesados'
    )
    
    # Rollback information
    puede_revertir = models.BooleanField(
        default=False,
        help_text='Indica si la operación puede ser revertida'
    )
    datos_rollback = models.JSONField(
        default=dict,
        blank=True,
        help_text='Datos necesarios para revertir la operación'
    )
    
    class Meta:
        verbose_name = 'Auditoría de Operación del Sistema'
        verbose_name_plural = 'Auditorías de Operaciones del Sistema'
        ordering = ['-fecha_auditoria']
        indexes = [
            # Primary audit indexes
            models.Index(fields=['accion', '-fecha_auditoria'], name='idx_aud_oper_accion_fecha'),
            models.Index(fields=['usuario_responsable', '-fecha_auditoria'], name='idx_aud_oper_usuario_fecha'),
            models.Index(fields=['exitosa', '-fecha_auditoria'], name='idx_aud_oper_exitosa_fecha'),
            
            # Performance and monitoring indexes
            models.Index(fields=['puede_revertir', '-fecha_auditoria'], name='idx_aud_oper_revert_fecha'),
            models.Index(fields=['duracion_segundos'], name='idx_aud_oper_duracion'),
            models.Index(fields=['registros_procesados'], name='idx_aud_oper_registros'),
            
            # System operation analysis indexes
            models.Index(fields=['accion', 'exitosa', '-fecha_auditoria'], name='idx_aud_oper_acc_exit_fecha'),
            models.Index(fields=['usuario_responsable', 'accion', '-fecha_auditoria'], name='idx_aud_oper_usr_acc_fecha'),
            models.Index(fields=['exitosa', 'puede_revertir', '-fecha_auditoria'], name='idx_aud_oper_exit_rev_fecha'),
            
            # Performance analysis indexes
            models.Index(fields=['accion', 'duracion_segundos', '-fecha_auditoria'], name='idx_aud_oper_acc_dur_fecha'),
            models.Index(fields=['registros_procesados', '-fecha_auditoria'], name='idx_aud_oper_reg_fecha'),
            
            # Error analysis indexes
            models.Index(fields=['exitosa', 'accion', '-fecha_auditoria'], name='idx_aud_oper_exit_acc_fecha'),
        ]
        constraints = [
            # Ensure duration is positive if provided
            models.CheckConstraint(
                check=models.Q(duracion_segundos__isnull=True) | models.Q(duracion_segundos__gte=0),
                name='audit_oper_duracion_positive'
            ),
            # Ensure processed records is non-negative if provided
            models.CheckConstraint(
                check=models.Q(registros_procesados__isnull=True) | models.Q(registros_procesados__gte=0),
                name='audit_oper_registros_non_negative'
            ),
        ]
    
    def __str__(self):
        status = "✓" if self.exitosa else "✗"
        return f"{status} {self.get_accion_display()} - {self.fecha_auditoria.strftime('%Y-%m-%d %H:%M')}"
    
    def get_operation_summary(self):
        """Get a human-readable summary of the operation"""
        status = "Exitosa" if self.exitosa else "Fallida"
        duration = f" ({self.duracion_segundos}s)" if self.duracion_segundos else ""
        return f"{self.get_accion_display()}: {status}{duration}"
    
    @classmethod
    def create_system_operation_audit(cls, accion, descripcion, user, entidades_afectadas=None,
                                    parametros_operacion=None, exitosa=True, errores=None,
                                    warnings=None, duracion_segundos=None, registros_procesados=None,
                                    puede_revertir=False, datos_rollback=None, ip_address=None,
                                    user_agent='', session_key='', contexto_adicional=None):
        """Create a system operation audit record"""
        if entidades_afectadas is None:
            entidades_afectadas = []
        if parametros_operacion is None:
            parametros_operacion = {}
        if errores is None:
            errores = []
        if warnings is None:
            warnings = []
        if datos_rollback is None:
            datos_rollback = {}
        if contexto_adicional is None:
            contexto_adicional = {}
        
        return cls.objects.create(
            accion=accion,
            descripcion=descripcion,
            usuario_responsable=user,
            entidades_afectadas=entidades_afectadas,
            parametros_operacion=parametros_operacion,
            exitosa=exitosa,
            errores=errores,
            warnings=warnings,
            duracion_segundos=duracion_segundos,
            registros_procesados=registros_procesados,
            puede_revertir=puede_revertir,
            datos_rollback=datos_rollback,
            direccion_ip=ip_address,
            user_agent=user_agent,
            session_key=session_key,
            contexto_adicional=contexto_adicional
        )


class AuditoriaAccesoSistema(AuditTrailBase):
    """
    Audit trail for system access and authentication events.
    Records login attempts, permission checks, and security events.
    """
    
    AUDIT_ACTIONS = [
        ('LOGIN_SUCCESS', 'Inicio de Sesión Exitoso'),
        ('LOGIN_FAILED', 'Inicio de Sesión Fallido'),
        ('LOGOUT', 'Cierre de Sesión'),
        ('PASSWORD_CHANGE', 'Cambio de Contraseña'),
        ('PERMISSION_CHECK', 'Verificación de Permisos'),
        ('UNAUTHORIZED_ACCESS', 'Acceso No Autorizado'),
        ('SESSION_EXPIRED', 'Sesión Expirada'),
        ('ACCOUNT_LOCKED', 'Cuenta Bloqueada'),
        ('ACCOUNT_UNLOCKED', 'Cuenta Desbloqueada'),
        ('SECURITY_VIOLATION', 'Violación de Seguridad'),
    ]
    
    # Access details
    accion = models.CharField(
        max_length=20,
        choices=AUDIT_ACTIONS,
        help_text='Tipo de evento de acceso'
    )
    usuario_objetivo = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='auditoria_acceso_objetivo',
        null=True,
        blank=True,
        help_text='Usuario objetivo del evento (puede ser diferente al responsable)'
    )
    
    # Access context
    recurso_accedido = models.CharField(
        max_length=200,
        blank=True,
        help_text='Recurso o URL accedida'
    )
    metodo_http = models.CharField(
        max_length=10,
        blank=True,
        help_text='Método HTTP utilizado'
    )
    codigo_respuesta = models.IntegerField(
        null=True,
        blank=True,
        help_text='Código de respuesta HTTP'
    )
    
    # Security information
    exitoso = models.BooleanField(
        default=True,
        help_text='Indica si el acceso fue exitoso'
    )
    motivo_fallo = models.TextField(
        blank=True,
        help_text='Motivo del fallo de acceso'
    )
    nivel_riesgo = models.CharField(
        max_length=10,
        choices=[
            ('BAJO', 'Bajo'),
            ('MEDIO', 'Medio'),
            ('ALTO', 'Alto'),
            ('CRITICO', 'Crítico'),
        ],
        default='BAJO',
        help_text='Nivel de riesgo del evento'
    )
    
    # Geographic and device information
    pais = models.CharField(
        max_length=100,
        blank=True,
        help_text='País desde donde se realizó el acceso'
    )
    ciudad = models.CharField(
        max_length=100,
        blank=True,
        help_text='Ciudad desde donde se realizó el acceso'
    )
    dispositivo = models.CharField(
        max_length=200,
        blank=True,
        help_text='Información del dispositivo utilizado'
    )
    
    class Meta:
        verbose_name = 'Auditoría de Acceso al Sistema'
        verbose_name_plural = 'Auditorías de Acceso al Sistema'
        ordering = ['-fecha_auditoria']
        indexes = [
            # Primary security audit indexes
            models.Index(fields=['accion', '-fecha_auditoria'], name='idx_aud_acc_accion_fecha'),
            models.Index(fields=['usuario_responsable', '-fecha_auditoria'], name='idx_aud_acc_usuario_fecha'),
            models.Index(fields=['usuario_objetivo', '-fecha_auditoria'], name='idx_aud_acc_objetivo_fecha'),
            models.Index(fields=['exitoso', '-fecha_auditoria'], name='idx_aud_acc_exitoso_fecha'),
            
            # Security monitoring indexes
            models.Index(fields=['nivel_riesgo', '-fecha_auditoria'], name='idx_aud_acc_riesgo_fecha'),
            models.Index(fields=['direccion_ip', '-fecha_auditoria'], name='idx_aud_acc_ip_fecha'),
            
            # Failed access tracking indexes
            models.Index(fields=['exitoso', 'accion', '-fecha_auditoria'], name='idx_aud_acc_exit_acc_fecha'),
            models.Index(fields=['exitoso', 'direccion_ip', '-fecha_auditoria'], name='idx_aud_acc_exit_ip_fecha'),
            models.Index(fields=['nivel_riesgo', 'exitoso', '-fecha_auditoria'], name='idx_aud_acc_risk_exit_fecha'),
            
            # Geographic and device tracking indexes
            models.Index(fields=['pais', '-fecha_auditoria'], name='idx_aud_acc_pais_fecha'),
            models.Index(fields=['ciudad', '-fecha_auditoria'], name='idx_aud_acc_ciudad_fecha'),
            
            # Security analysis indexes
            models.Index(fields=['usuario_responsable', 'exitoso', '-fecha_auditoria'], name='idx_aud_acc_usr_exit_fecha'),
            models.Index(fields=['accion', 'nivel_riesgo', '-fecha_auditoria'], name='idx_aud_acc_acc_risk_fecha'),
            models.Index(fields=['direccion_ip', 'exitoso', '-fecha_auditoria'], name='idx_aud_acc_ip_exit_fecha'),
            
            # HTTP request tracking indexes
            models.Index(fields=['recurso_accedido', '-fecha_auditoria'], name='idx_aud_acc_recurso_fecha'),
            models.Index(fields=['metodo_http', 'codigo_respuesta', '-fecha_auditoria'], name='idx_aud_acc_http_fecha'),
        ]
        constraints = [
            # Ensure HTTP response codes are valid if provided
            models.CheckConstraint(
                check=models.Q(codigo_respuesta__isnull=True) | 
                      models.Q(codigo_respuesta__gte=100, codigo_respuesta__lt=600),
                name='audit_acceso_codigo_respuesta_valid'
            ),
        ]
    
    def __str__(self):
        status = "✓" if self.exitoso else "✗"
        user = self.usuario_objetivo or self.usuario_responsable
        return f"{status} {self.get_accion_display()} - {user.username} - {self.fecha_auditoria.strftime('%Y-%m-%d %H:%M')}"
    
    def get_access_summary(self):
        """Get a human-readable summary of the access event"""
        status = "Exitoso" if self.exitoso else "Fallido"
        risk = f" (Riesgo: {self.get_nivel_riesgo_display()})" if self.nivel_riesgo != 'BAJO' else ""
        return f"{self.get_accion_display()}: {status}{risk}"
    
    @classmethod
    def create_access_audit(cls, accion, user, usuario_objetivo=None, recurso_accedido='',
                          metodo_http='', codigo_respuesta=None, exitoso=True, motivo_fallo='',
                          nivel_riesgo='BAJO', pais='', ciudad='', dispositivo='',
                          ip_address=None, user_agent='', session_key='', contexto_adicional=None):
        """Create an access audit record"""
        if contexto_adicional is None:
            contexto_adicional = {}
        
        return cls.objects.create(
            accion=accion,
            usuario_responsable=user,
            usuario_objetivo=usuario_objetivo,
            recurso_accedido=recurso_accedido,
            metodo_http=metodo_http,
            codigo_respuesta=codigo_respuesta,
            exitoso=exitoso,
            motivo_fallo=motivo_fallo,
            nivel_riesgo=nivel_riesgo,
            pais=pais,
            ciudad=ciudad,
            dispositivo=dispositivo,
            direccion_ip=ip_address,
            user_agent=user_agent,
            session_key=session_key,
            contexto_adicional=contexto_adicional
        )