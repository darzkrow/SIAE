from django.db import models
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
        
        # Create audit record for state changes
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
        Validate state transitions according to business rules.
        """
        valid_transitions = {
            'EN_ALMACEN': ['EN_TRANSITO', 'INSTALADO', 'MANTENIMIENTO'],
            'EN_TRANSITO': ['EN_ALMACEN', 'INSTALADO'],
            'INSTALADO': ['EN_USO', 'MANTENIMIENTO', 'EN_ALMACEN'],
            'EN_USO': ['MANTENIMIENTO', 'EN_ALMACEN'],
            'MANTENIMIENTO': ['EN_ALMACEN', 'INSTALADO', 'EN_USO'],
        }
        
        return to_state in valid_transitions.get(from_state, [])
    
    def create_state_change_audit(self, old_state, new_state):
        """Create audit record for state changes"""
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


class HistorialMovimientoActivo(models.Model):
    """
    Immutable record of all asset movements and state changes.
    Provides complete audit trail for asset traceability.
    """
    
    MOVEMENT_TYPES = [
        ('INGRESO_INICIAL', 'Ingreso Inicial'),
        ('TRASLADO_ALMACEN', 'Traslado entre Almacenes'),
        ('CAMBIO_ESTADO', 'Cambio de Estado'),
        ('INSTALACION', 'Instalación'),
        ('RETIRO', 'Retiro'),
        ('MANTENIMIENTO_ENTRADA', 'Entrada a Mantenimiento'),
        ('MANTENIMIENTO_SALIDA', 'Salida de Mantenimiento'),
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
        max_length=30,
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
    
    class Meta:
        verbose_name = 'Historial de Movimiento de Activo'
        verbose_name_plural = 'Historial de Movimientos de Activos'
        ordering = ['-fecha_movimiento']
        indexes = [
            models.Index(fields=['activo', '-fecha_movimiento']),
            models.Index(fields=['almacen_origen', '-fecha_movimiento']),
            models.Index(fields=['almacen_destino', '-fecha_movimiento']),
            models.Index(fields=['tipo_movimiento', '-fecha_movimiento']),
            models.Index(fields=['usuario_responsable', '-fecha_movimiento']),
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
        """Override save to ensure validation and immutability"""
        # Prevent modification of existing records (immutable audit trail)
        if self.pk:
            raise ValidationError(
                'Los registros de historial de movimientos no pueden ser modificados'
            )
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def create_movement_record(cls, activo, tipo_movimiento, usuario_responsable, 
                             motivo, almacen_origen=None, almacen_destino=None,
                             estado_anterior=None, estado_nuevo=None,
                             observaciones='', solicitud_traslado=None):
        """
        Create a new movement record with proper validation.
        """
        # Get current state if not provided
        if estado_anterior is None:
            estado_anterior = activo.estado
        if estado_nuevo is None:
            estado_nuevo = activo.estado
        
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
            solicitud_traslado=solicitud_traslado
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
        ]
    
    def __str__(self):
        return f"{self.numero_solicitud} - {self.activo.codigo_actual} ({self.almacen_origen.prefijo} → {self.almacen_destino.prefijo})"
    
    def clean(self):
        """Custom validation for transfer requests"""
        from django.core.exceptions import ValidationError
        
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
        
        # Validate that asset is not in transit
        if self.activo and self.activo.estado == 'EN_TRANSITO':
            raise ValidationError(
                'No se pueden crear solicitudes de traslado para activos en tránsito'
            )
    
    def save(self, *args, **kwargs):
        """Override save to generate request number and validate"""
        if not self.numero_solicitud:
            self.numero_solicitud = self.generate_request_number()
        
        self.full_clean()
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
                self.aprobacion_destino)
    
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
    
    def execute_transfer(self, executor):
        """Execute the approved transfer"""
        if not self.can_execute():
            raise ValidationError('La solicitud no puede ser ejecutada')
        
        from django.utils import timezone
        
        # Update asset code and location
        old_code, new_code = self.activo.evolve_asset_code(self.almacen_destino)
        self.activo.almacen_actual = self.almacen_destino
        self.activo.estado = 'EN_TRANSITO'
        self.activo.save()
        
        # Create movement record
        HistorialMovimientoActivo.create_movement_record(
            activo=self.activo,
            tipo_movimiento='TRASLADO_ALMACEN',
            usuario_responsable=executor,
            motivo=self.motivo,
            almacen_origen=self.almacen_origen,
            almacen_destino=self.almacen_destino,
            estado_anterior='EN_ALMACEN',
            estado_nuevo='EN_TRANSITO',
            observaciones=f'Solicitud: {self.numero_solicitud}',
            solicitud_traslado=self
        )
        
        # Update request status
        self.estado = 'EN_TRANSITO'
        self.fecha_ejecucion = timezone.now()
        self.ejecutado_por = executor
        self.save()
    
    def complete_transfer(self, receiver):
        """Complete the transfer when asset arrives at destination"""
        if self.estado != 'EN_TRANSITO':
            raise ValidationError('Solo se pueden completar traslados en tránsito')
        
        from django.utils import timezone
        
        # Update asset state
        self.activo.estado = 'EN_ALMACEN'
        self.activo.save()
        
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
        """Override save to ensure validation"""
        self.full_clean()
        super().save(*args, **kwargs)


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
