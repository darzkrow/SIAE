from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from core.models import TimeStampedModel
from django.urls import reverse
import qrcode
from io import BytesIO
from django.core.files import File
import re
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

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
        'institucion.AlmacenRegional',
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
        from .states import AssetStateManager
        
        is_valid, _ = AssetStateManager.validate_state_transition(from_state, to_state)
        return is_valid
    
    def create_state_change_audit(self, old_state, new_state):
        """Create audit record for state changes using AssetStateManager"""
        from .states import AssetStateAuditLogger
        
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
        """
        from .states import AssetStateManager
        
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
        """
        from .states import AssetStateManager
        
        return AssetStateManager.get_allowed_transitions(self.estado)
    
    def can_be_transferred(self):
        """
        Check if asset can be included in a transfer request.
        """
        from .states import AssetStateManager
        
        return AssetStateManager.validate_transfer_request_state(self)
    
    def get_state_history(self, limit: int = 10):
        """
        Get state transition history for this asset.
        """
        from .states import AssetStateManager
        
        return AssetStateManager.get_state_transition_history(self, limit)


class HistorialMovimientoActivo(models.Model):
    """
    Immutable record of all asset movements and state changes.
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
        'institucion.AlmacenRegional',
        on_delete=models.CASCADE,
        related_name='movimientos_origen',
        null=True,
        blank=True,
        help_text='Almacén de origen (si aplica)'
    )
    almacen_destino = models.ForeignKey(
        'institucion.AlmacenRegional',
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
            models.Index(fields=['activo', '-fecha_movimiento'], name='idx_hist_activo_fecha'),
            models.Index(fields=['almacen_origen', '-fecha_movimiento'], name='idx_hist_origen_fecha'),
            models.Index(fields=['almacen_destino', '-fecha_movimiento'], name='idx_hist_destino_fecha'),
            models.Index(fields=['tipo_movimiento', '-fecha_movimiento'], name='idx_hist_tipo_fecha'),
            models.Index(fields=['usuario_responsable', '-fecha_movimiento'], name='idx_hist_usuario_fecha'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(fecha_movimiento__isnull=False),
                name='operaciones_hist_fecha_mov'
            ),
        ]
    
    def __str__(self):
        return f"{self.activo.codigo_actual} - {self.get_tipo_movimiento_display()} - {self.fecha_movimiento.strftime('%y-%m-%d %H:%M')}"
    
    def clean(self):
        """Custom validation for movement records"""
        if self.tipo_movimiento == 'TRASLADO_ALMACEN':
            if not (self.almacen_origen and self.almacen_destino):
                raise ValidationError('Los traslados entre almacenes requieren almacén origen y destino')
            if self.almacen_origen == self.almacen_destino:
                raise ValidationError('El almacén origen y destino no pueden ser el mismo')
        
        if not ActivoInventario.is_valid_state_transition(self.estado_anterior, self.estado_nuevo):
            raise ValidationError(f'Transición de estado inválida: {self.estado_anterior} → {self.estado_nuevo}')
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation and immutability."""
        if self.pk:
            raise ValidationError('Los registros de historial de movimientos son inmutables.')
        
        if not self.activo:
            raise ValidationError('El activo es requerido')
        
        if not self.usuario_responsable:
            raise ValidationError('El usuario responsable es requerido')
        
        self.full_clean()
        
        if not self.fecha_movimiento:
            self.fecha_movimiento = timezone.now()
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Override delete to prevent deletion of audit records."""
        raise ValidationError('Los registros de historial de movimientos no pueden ser eliminados.')
    
    @classmethod
    def create_movement_record(cls, activo, tipo_movimiento, usuario_responsable, 
                             motivo, almacen_origen=None, almacen_destino=None,
                             estado_anterior=None, estado_nuevo=None,
                             observaciones='', solicitud_traslado=None, metadata=None):
        """Create a new movement record with proper validation."""
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
            codigo_nuevo=activo.codigo_actual,
            usuario_responsable=usuario_responsable,
            motivo=motivo,
            observaciones=observaciones,
            solicitud_traslado=solicitud_traslado,
            metadata=metadata
        )


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
    
    PRIORITIES = [
        ('BAJA', 'Baja'),
        ('NORMAL', 'Normal'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]
    
    # Unique identifier for the transfer request
    numero_solicitud = models.CharField(
        max_length=20,
        unique=True,
        help_text='Número de solicitud único generado automáticamente'
    )
    
    # Asset and locations
    activo = models.ForeignKey(
        ActivoInventario,
        on_delete=models.CASCADE,
        related_name='solicitudes_traslado',
        help_text='Activo a trasladar'
    )
    almacen_origen = models.ForeignKey(
        'institucion.AlmacenRegional',
        on_delete=models.CASCADE,
        related_name='traslados_salida',
        help_text='Almacén de origen'
    )
    almacen_destino = models.ForeignKey(
        'institucion.AlmacenRegional',
        on_delete=models.CASCADE,
        related_name='traslados_entrada',
        help_text='Almacén de destino'
    )
    
    # Workflow status
    estado = models.CharField(
        max_length=20,
        choices=TRANSFER_STATES,
        default='PENDIENTE',
        help_text='Estado actual del flujo de aprobación'
    )
    prioridad = models.CharField(
        max_length=10,
        choices=PRIORITIES,
        default='NORMAL',
        help_text='Prioridad del traslado'
    )
    
    # People involved
    solicitante = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='traslados_solicitados',
        help_text='Usuario que solicita el traslado'
    )
    ejecutor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='traslados_ejecutados',
        help_text='Usuario que ejecuta el traslado físico'
    )
    
    # Approval tracking
    aprobacion_origen = models.OneToOneField(
        'AprobacionTraslado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitud_origen',
        help_text='Aprobación del almacén de origen'
    )
    aprobacion_destino = models.OneToOneField(
        'AprobacionTraslado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitud_destino',
        help_text='Aprobación del almacén de destino'
    )
    
    # Timestamps and details
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_ejecucion = models.DateTimeField(null=True, blank=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    fecha_limite = models.DateTimeField(help_text='Fecha máxima para completar el traslado')
    
    motivo = models.TextField(help_text='Motivo detallado del traslado')
    observaciones = models.TextField(blank=True, help_text='Observaciones adicionales')
    
    # QR Code for physical validation
    qr_code = models.ImageField(upload_to='qrcodes/transfers/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Solicitud de Traslado'
        verbose_name_plural = 'Solicitudes de Traslado'
        ordering = ['-fecha_solicitud']
        indexes = [
            models.Index(fields=['estado', '-fecha_solicitud']),
            models.Index(fields=['numero_solicitud']),
            models.Index(fields=['almacen_origen', 'estado']),
            models.Index(fields=['almacen_destino', 'estado']),
            models.Index(fields=['prioridad', 'estado']),
            models.Index(fields=['fecha_limite']),
            # Composite indexes for approval workflow
            models.Index(fields=['aprobacion_origen', 'estado']),
            models.Index(fields=['aprobacion_destino', 'estado']),
            models.Index(fields=['estado', 'fecha_limite']),
        ]
    
    def __str__(self):
        return f"{self.numero_solicitud} - {self.activo.codigo_actual} ({self.get_estado_display()})"
    
    def clean(self):
        """Custom validation for transfer request"""
        if self.almacen_origen == self.almacen_destino:
            raise ValidationError('El almacén origen y destino no pueden ser el mismo')
        
        if self.activo.almacen_actual != self.almacen_origen:
            raise ValidationError(f'El activo no se encuentra en el almacén de origen especificado')
        
        # Validate that asset can be transferred using state management system
        can_transfer, message = self.activo.can_be_transferred()
        if not can_transfer:
            raise ValidationError(f'El activo no puede ser trasladado: {message}')
        
        if self.fecha_limite and self.fecha_limite <= timezone.now():
            raise ValidationError('La fecha límite debe ser futura')
    
    def save(self, *args, **kwargs):
        """Override save to generate request number and QR code"""
        if not self.numero_solicitud:
            self.numero_solicitud = self.generate_request_number()
        
        # Set executive user if in transition
        if self.estado == 'EN_TRANSITO' and not self.fecha_ejecucion:
            self.fecha_ejecucion = timezone.now()
        
        # Generation of QR code
        if not self.qr_code:
            self.generate_qr_code()
            
        super().save(*args, **kwargs)
    
    def generate_request_number(self):
        """Generate a unique request number: TR-{YEAR}-{SEQUENCE}"""
        year = timezone.now().year
        last_request = SolicitudTraslado.objects.filter(
            numero_solicitud__startswith=f'TR-{year}'
        ).order_by('numero_solicitud').last()
        
        if last_request:
            last_number = int(last_request.numero_solicitud.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
            
        return f"TR-{year}-{new_number:06d}"
    
    def generate_qr_code(self):
        """Generate QR code containing transfer information"""
        qr_data = f"Solicitud: {self.numero_solicitud}\nActivo: {self.activo.codigo_actual}\nDesde: {self.almacen_origen.prefijo}\nHacia: {self.almacen_destino.prefijo}\nEstado: {self.estado}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        file_name = f"qr_{self.numero_solicitud}.png"
        self.qr_code.save(file_name, File(buffer), save=False)
    
    @transaction.atomic
    def execute_transfer(self, executor):
        """
        Execute the physical transfer. 
        Updates asset status and evolves its code.
        """
        if not self.can_execute():
            raise ValidationError('La solicitud no está lista para ser ejecutada (requiere doble aprobación)')
        
        execution_start_time = timezone.now()
        
        try:
            # Update solicitud state
            self.estado = 'EN_TRANSITO'
            self.ejecutor = executor
            self.fecha_ejecucion = execution_start_time
            self.save()
            
            # Evolve asset code and update asset status
            old_code = self.activo.codigo_actual
            old_code, new_code = self.activo.evolve_asset_code(self.almacen_destino)
            
            # Update asset
            self.activo.estado = 'EN_TRANSITO'
            self.activo.save()
            
            # Create movement history record
            movement = HistorialMovimientoActivo.create_movement_record(
                activo=self.activo,
                tipo_movimiento='TRASLADO_EJECUTADO',
                usuario_responsable=executor,
                motivo=f'Ejecución de traslado {self.numero_solicitud}',
                almacen_origen=self.almacen_origen,
                almacen_destino=self.almacen_destino,
                estado_anterior='EN_ALMACEN',
                estado_nuevo='EN_TRANSITO',
                solicitud_traslado=self,
                metadata={
                    'codigo_anterior': old_code,
                    'codigo_nuevo': new_code,
                    'execution_time': execution_start_time.isoformat()
                }
            )
            
            # Update movement code records (since create_movement_record uses current code)
            movement.codigo_anterior = old_code
            movement.codigo_nuevo = new_code
            movement.save()
            
            # Create audit log entry for this operation
            # This is a complex operation with multiple steps
            execution_duration = (timezone.now() - execution_start_time).total_seconds()
            
            # Rollback data for manual correction if needed
            rollback_data = {
                'old_code': old_code,
                'new_code': new_code,
                'old_state': 'EN_ALMACEN',
                'old_warehouse_id': self.almacen_origen.id,
                'solicitud_id': self.id
            }
            
            # Record systemic audit
            from .services import AuditTrailService
            AuditTrailService.record_operation_success(
                accion='TRANSFER_EXECUTE',
                descripcion=f"Ejecución de traslado {self.numero_solicitud} para activo {old_code}",
                user=executor,
                entidades_afectadas=[
                    f"ActivoInventario:{self.activo.id}",
                    f"SolicitudTraslado:{self.id}"
                ],
                parametros_operacion={
                    'numero_solicitud': self.numero_solicitud,
                    'codigo_original': self.activo.codigo_original,
                    'codigo_previo': old_code,
                    'codigo_nuevo': new_code
                },
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
            logger.error(f"Transfer execution failed for {self.numero_solicitud}: {str(e)}")
            
            # Record systemic failure
            from .services import AuditTrailService
            AuditTrailService.record_operation_failure(
                accion='TRANSFER_EXECUTE',
                descripcion=f"Error ejecutando traslado {self.numero_solicitud}",
                user=executor,
                errores=[str(e)],
                parametros_operacion={
                    'numero_solicitud': self.numero_solicitud,
                    'activo_id': self.activo.id
                }
            )
            
            # Re-raise to trigger transaction rollback
            raise
    
    @transaction.atomic
    def complete_transfer(self, receiver):
        """Complete the transfer when asset arrives at destination"""
        if self.estado != 'EN_TRANSITO':
            raise ValidationError('Solo se pueden completar traslados que estén en tránsito')
        
        # Update solicitud state
        self.estado = 'COMPLETADA'
        self.fecha_completado = timezone.now()
        self.save()
        
        # Update asset location and state
        self.activo.almacen_actual = self.almacen_destino
        self.activo.estado = 'EN_ALMACEN'
        self.activo.save()
        
        # Create completion movement record
        HistorialMovimientoActivo.create_movement_record(
            activo=self.activo,
            tipo_movimiento='CAMBIO_ESTADO_AUTO_TRANSFER_COMPLETED',
            usuario_responsable=receiver,
            motivo=f'Llegada a destino - Traslado {self.numero_solicitud} completado',
            almacen_origen=self.almacen_origen,
            almacen_destino=self.almacen_destino,
            estado_anterior='EN_TRANSITO',
            estado_nuevo='EN_ALMACEN',
            solicitud_traslado=self
        )
        
        # Record systemic audit
        from .services import AuditTrailService
        AuditTrailService.record_operation_success(
            accion='TRANSFER_COMPLETE',
            descripcion=f"Completado de traslado {self.numero_solicitud} para activo {self.activo.codigo_actual}",
            user=receiver,
            entidades_afectadas=[
                f"ActivoInventario:{self.activo.id}",
                f"SolicitudTraslado:{self.id}"
            ],
            parametros_operacion={
                'numero_solicitud': self.numero_solicitud,
                'codigo_actual': self.activo.codigo_actual,
                'almacen_destino': self.almacen_destino.prefijo
            },
            registros_procesados=1
        )
    
    def cancel_request(self, user, reason):
        """Cancel the transfer request"""
        if not self.can_be_cancelled():
            raise ValidationError(f'No se puede cancelar la solicitud en su estado actual: {self.get_estado_display()}')
            
        self.estado = 'CANCELADA'
        self.observaciones = f"{self.observaciones}\n\nCANCELADA por {user.username}. Motivo: {reason}"
        self.save()
        
        # Record systemic audit
        from .services import AuditTrailService
        AuditTrailService.record_operation_success(
            accion='TRANSFER_CANCEL',
            descripcion=f"Cancelación de traslado {self.numero_solicitud}",
            user=user,
            entidades_afectadas=[f"SolicitudTraslado:{self.id}"],
            parametros_operacion={
                'numero_solicitud': self.numero_solicitud,
                'motivo_cancelacion': reason
            }
        )
    
    def can_execute(self):
        """Check if request is ready for execution (Double approval required)"""
        if self.estado not in ['APROBADA_COMPLETA', 'EN_TRANSITO']:
            return False
            
        # Verify both approvals are present and favorable
        if not (self.aprobacion_origen and self.aprobacion_origen.decision == 'APROBADO'):
            return False
        if not (self.aprobacion_destino and self.aprobacion_destino.decision == 'APROBADO'):
            return False
            
        return True
    
    def can_be_cancelled(self):
        """Check if request can be cancelled"""
        return self.estado in ['PENDIENTE', 'APROBADA_ORIGEN', 'APROBADA_DESTINO', 'APROBADA_COMPLETA']
    
    def is_overdue(self):
        """Check if request is overdue"""
        if self.estado in ['COMPLETADA', 'CANCELADA', 'RECHAZADA']:
            return False
        return timezone.now() > self.fecha_limite
    
    def get_days_until_deadline(self):
        """Get days until deadline (negative if overdue)"""
        return (self.fecha_limite - timezone.now()).days

    def get_approval_status(self):
        """Get detailed approval status"""
        return {
            'origen': self.aprobacion_origen.decision if self.aprobacion_origen else None,
            'destino': self.aprobacion_destino.decision if self.aprobacion_destino else None,
            'completa': self.estado == 'APROBADA_COMPLETA',
            'pendiente_origen': self.aprobacion_origen is None,
            'pendiente_destino': self.aprobacion_destino is None
        }

    @classmethod
    def get_pending_for_manager(cls, manager):
        """Get pending requests awaiting approval from a specific manager"""
        from django.db.models import Q
        return cls.objects.filter(
            Q(almacen_origen__manager=manager, aprobacion_origen__isnull=True) |
            Q(almacen_destino__manager=manager, aprobacion_destino__isnull=True),
            estado__in=['PENDIENTE', 'APROBADA_ORIGEN', 'APROBADA_DESTINO']
        ).distinct()


class AprobacionTraslado(models.Model):
    """ Record of approval/rejection decision by a warehouse manager """
    
    DECISION_CHOICES = [
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]
    
    TYPE_CHOICES = [
        ('ORIGEN', 'Origen'),
        ('DESTINO', 'Destino'),
    ]
    
    solicitud = models.ForeignKey(
        SolicitudTraslado,
        on_delete=models.CASCADE,
        related_name='aprobaciones',
        help_text='Solicitud a la que pertenece esta aprobación'
    )
    aprobador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        help_text='Gerente que tomó la decisión'
    )
    tipo_aprobacion = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        help_text='Indica si aprueba como origen o como destino'
    )
    decision = models.CharField(
        max_length=10,
        choices=DECISION_CHOICES,
        help_text='Decisión tomada'
    )
    fecha_decision = models.DateTimeField(auto_now_add=True)
    comentarios = models.TextField(blank=True, help_text='Comentarios sobre la decisión')
    
    class Meta:
        verbose_name = 'Aprobación de Traslado'
        verbose_name_plural = 'Aprobaciones de Traslado'
        unique_together = ('solicitud', 'tipo_aprobacion')
        ordering = ['-fecha_decision']
        indexes = [
            models.Index(fields=['solicitud', 'tipo_aprobacion']),
            models.Index(fields=['aprobador', 'decision']),
            models.Index(fields=['fecha_decision']),
        ]
    
    def __str__(self):
        return f"{self.solicitud.numero_solicitud} - {self.get_tipo_aprobacion_display()}: {self.decision}"
    
    def save(self, *args, **kwargs):
        """Update SolicitudTraslado state based on dual approval rule"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Associate this approval with the solicitud
            if self.tipo_aprobacion == 'ORIGEN':
                self.solicitud.aprobacion_origen = self
            else:
                self.solicitud.aprobacion_destino = self
            
            # Update workflow state
            if self.decision == 'RECHAZADO':
                self.solicitud.estado = 'RECHAZADA'
            else:
                # Check for double approval
                status = self.solicitud.get_approval_status()
                if status['origen'] == 'APROBADO' and status['destino'] == 'APROBADO':
                    self.solicitud.estado = 'APROBADA_COMPLETA'
                elif self.tipo_aprobacion == 'ORIGEN':
                    self.solicitud.estado = 'APROBADA_ORIGEN'
                else:
                    self.solicitud.estado = 'APROBADA_DESTINO'
            
            self.solicitud.save()


# ============================================================================
# COMPREHENSIVE AUDIT TRAIL MODELS
# ============================================================================

class AuditTrailBase(models.Model):
    """
    Base class for all audit trail models.
    """
    
    fecha_auditoria = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha y hora del evento'
    )
    usuario_responsable = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_responsable',
        help_text='Usuario que realizó la acción'
    )
    
    # Technical context
    direccion_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='Dirección IP desde donde se realizó la acción'
    )
    user_agent = models.TextField(
        blank=True,
        help_text='Información del navegador/cliente'
    )
    session_key = models.CharField(
        max_length=40,
        blank=True,
        help_text='ID de sesión de Django'
    )
    
    # Internal checksum for integrity
    checksum = models.CharField(
        max_length=64,
        blank=True,
        help_text='Hash de integridad del registro'
    )
    
    # Additional generic context
    contexto_adicional = models.JSONField(
        default=dict,
        blank=True,
        help_text='Contexto adicional de la operación en formato JSON'
    )
    
    class Meta:
        abstract = True
        ordering = ['-fecha_auditoria']
        indexes = [
            models.Index(fields=['-fecha_auditoria'], name='%(class)s_fecha_idx'),
            models.Index(fields=['usuario_responsable', '-fecha_auditoria'], name='%(class)s_usr_fecha_idx'),
            models.Index(fields=['direccion_ip', '-fecha_auditoria'], name='%(class)s_ip_fecha_idx'),
            models.Index(fields=['session_key', '-fecha_auditoria'], name='%(class)s_sess_fecha_idx'),
        ]

    def save(self, *args, **kwargs):
        """Ensure immutability and calculate checksum"""
        if self.pk:
            raise ValidationError('Los registros de auditoría son inmutables.')
        
        # Calculate checksum before saving
        if not self.checksum:
            self.checksum = self.calculate_checksum()
            
        super().save(*args, **kwargs)

    def calculate_checksum(self):
        """Calculate HMAC/SHA256 checksum of the record fields for integrity"""
        import hashlib
        import json
        
        # Collect relevant fields
        relevant_data = {
            'fecha': self.fecha_auditoria.isoformat() if self.fecha_auditoria else '',
            'usuario_id': self.usuario_responsable_id,
            'ip': self.direccion_ip or '',
            'session': self.session_key or '',
            'contexto': json.dumps(self.contexto_adicional, sort_keys=True)
        }
        
        # Add model specific fields if implemented
        relevant_data.update(self.get_checksum_data())
        
        data_string = json.dumps(relevant_data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()

    def get_checksum_data(self):
        """Override in subclasses to include model-specific fields in checksum"""
        return {}


class AuditoriaEstadoActivo(AuditTrailBase):
    """
    Audit trail for asset state changes.
    """
    
    activo = models.ForeignKey(
        ActivoInventario,
        on_delete=models.CASCADE,
        related_name='auditoria_estados',
        help_text='Activo que cambió de estado'
    )
    estado_anterior = models.CharField(
        max_length=20,
        choices=ActivoInventario.ASSET_STATES,
        help_text='Estado antes del cambio'
    )
    estado_nuevo = models.CharField(
        max_length=20,
        choices=ActivoInventario.ASSET_STATES,
        help_text='Estado después del cambio'
    )
    motivo = models.TextField(
        help_text='Motivo del cambio de estado'
    )
    exitoso = models.BooleanField(
        default=True,
        help_text='Indica si el cambio fue exitoso o fallido (por validación)'
    )

    class Meta:
        verbose_name = 'Auditoría de Estado de Activo'
        verbose_name_plural = 'Auditorías de Estados de Activos'
        ordering = ['-fecha_auditoria']
        indexes = [
            models.Index(fields=['activo', '-fecha_auditoria'], name='idx_aud_est_activo_fecha'),
            models.Index(fields=['estado_nuevo', '-fecha_auditoria'], name='idx_aud_est_nuevo_fecha'),
            models.Index(fields=['exitoso', '-fecha_auditoria'], name='idx_aud_est_exitoso_fecha'),
        ]

    def get_checksum_data(self):
        return {
            'activo_id': self.activo_id,
            'anterior': self.estado_anterior,
            'nuevo': self.estado_nuevo,
            'exitoso': self.exitoso
        }

    @classmethod
    def create_audit(cls, activo, old_state, new_state, user, motivo, exitoso=True, 
                    ip_address=None, user_agent='', session_key='', contexto_adicional=None):
        """Create a state change audit record"""
        if contexto_adicional is None:
            contexto_adicional = {}
            
        return cls.objects.create(
            activo=activo,
            estado_anterior=old_state,
            estado_nuevo=new_state,
            usuario_responsable=user,
            motivo=motivo,
            exitoso=exitoso,
            direccion_ip=ip_address,
            user_agent=user_agent,
            session_key=session_key,
            contexto_adicional=contexto_adicional
        )


class AuditoriaAprobacion(AuditTrailBase):
    """
    Audit trail for transfer approval decisions.
    """
    
    solicitud_traslado = models.ForeignKey(
        SolicitudTraslado,
        on_delete=models.CASCADE,
        related_name='auditoria_aprobaciones',
        help_text='Solicitud en la que se tomó la decisión'
    )
    aprobacion = models.ForeignKey(
        AprobacionTraslado,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='Vínculo al registro de aprobación (si fue exitosa)'
    )
    
    # Action context
    accion = models.CharField(
        max_length=20,
        choices=[
            ('APPROVAL_GRANTED', 'Aprobación Otorgada'),
            ('APPROVAL_REJECTED', 'Aprobación Rechazada'),
            ('APPROVAL_REVOKED', 'Aprobación Revocada'),
        ],
        help_text='Tipo de acción realizada'
    )
    comentarios = models.TextField(
        blank=True,
        help_text='Comentarios del aprobador'
    )
    
    # Rejection specific info
    motivo_rechazo = models.TextField(
        blank=True,
        help_text='Motivo técnico del rechazo'
    )

    class Meta:
        verbose_name = 'Auditoría de Aprobación'
        verbose_name_plural = 'Auditorías de Aprobaciones'
        ordering = ['-fecha_auditoria']
        indexes = [
            models.Index(fields=['solicitud_traslado', '-fecha_auditoria'], name='idx_aud_apr_sol_fecha'),
            models.Index(fields=['accion', '-fecha_auditoria'], name='idx_aud_apr_acc_fecha'),
            models.Index(fields=['aprobacion', '-fecha_auditoria'], name='idx_aud_apr_apr_fecha'),
        ]

    def get_checksum_data(self):
        return {
            'solicitud_id': self.solicitud_traslado_id,
            'accion': self.accion,
            'aprobacion_id': self.aprobacion_id if self.aprobacion_id else 0
        }

    @classmethod
    def create_audit(cls, solicitud, accion, user, aprobacion=None, comentarios='', 
                    motivo_rechazo='', ip_address=None, user_agent='', 
                    session_key='', contexto_adicional=None):
        """Create an approval audit record"""
        if contexto_adicional is None:
            contexto_adicional = {}
            
        return cls.objects.create(
            solicitud_traslado=solicitud,
            aprobacion=aprobacion,
            accion=accion,
            usuario_responsable=user,
            comentarios=comentarios,
            motivo_rechazo=motivo_rechazo,
            direccion_ip=ip_address,
            user_agent=user_agent,
            session_key=session_key,
            contexto_adicional=contexto_adicional
        )


class AuditoriaOperacionSistema(AuditTrailBase):
    """
    Audit trail for complex systemic operations (transfers, inventory sync, batch processing).
    """
    
    accion = models.CharField(
        max_length=50,
        help_text='Identificador de la operación (ej. TRANSFER_EXECUTE)'
    )
    descripcion = models.TextField(
        help_text='Descripción detallada de la operación'
    )
    
    # Impact tracing
    entidades_afectadas = models.JSONField(
        default=list,
        help_text='Lista de entidades (Modelo:ID) alteradas por la operación'
    )
    parametros_operacion = models.JSONField(
        default=dict,
        help_text='Parámetros de entrada de la operación'
    )
    
    # Result information
    exitosa = models.BooleanField(
        default=True,
        help_text='Indica si la operación terminó correctamente'
    )
    errores = models.JSONField(
        default=list,
        blank=True,
        help_text='Lista de errores ocurridos (si falló)'
    )
    warnings = models.JSONField(
        default=list,
        blank=True,
        help_text='Lista de advertencias ocurridas'
    )
    
    # Performance metrics
    duracion_segundos = models.FloatField(
        null=True,
        blank=True,
        help_text='Duración de la operación en segundos'
    )
    registros_procesados = models.IntegerField(
        default=0,
        help_text='Número total de registros afectados'
    )
    
    # Rollback information
    puede_revertir = models.BooleanField(
        default=False,
        help_text='Indica si la operación tiene lógica de reversión'
    )
    datos_rollback = models.JSONField(
        default=dict,
        blank=True,
        help_text='Datos necesarios para ejecutar un rollback'
    )

    class Meta:
        verbose_name = 'Auditoría de Operación de Sistema'
        verbose_name_plural = 'Auditorías de Operaciones de Sistema'
        ordering = ['-fecha_auditoria']
        indexes = [
            models.Index(fields=['accion', '-fecha_auditoria'], name='idx_aud_op_acc_fecha'),
            models.Index(fields=['exitosa', '-fecha_auditoria'], name='idx_aud_op_exit_fecha'),
            models.Index(fields=['puede_revertir', '-fecha_auditoria'], name='idx_aud_op_rev_fecha'),
        ]

    def get_checksum_data(self):
        import json
        return {
            'accion': self.accion,
            'exitosa': self.exitosa,
            'registros': self.registros_procesados,
            'entidades': json.dumps(self.entidades_afectadas, sort_keys=True)
        }

    @classmethod
    def create_audit(cls, accion, descripcion, user, entidades_afectadas=None, 
                    parametros_operacion=None, exitosa=True, errores=None, 
                    warnings=None, duracion_segundos=None, registros_procesados=0,
                    puede_revertir=False, datos_rollback=None, ip_address=None, 
                    user_agent='', session_key='', contexto_adicional=None):
        """Create a systemic operation audit record"""
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
        help_text='Usuario objetivo del evento'
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
            models.Index(fields=['accion', '-fecha_auditoria'], name='idx_aud_acc_accion_fecha'),
            models.Index(fields=['usuario_responsable', '-fecha_auditoria'], name='idx_aud_acc_usuario_fecha'),
            models.Index(fields=['usuario_objetivo', '-fecha_auditoria'], name='idx_aud_acc_objetivo_fecha'),
            models.Index(fields=['exitoso', '-fecha_auditoria'], name='idx_aud_acc_exitoso_fecha'),
            models.Index(fields=['nivel_riesgo', '-fecha_auditoria'], name='idx_aud_acc_riesgo_fecha'),
            models.Index(fields=['direccion_ip', '-fecha_auditoria'], name='idx_aud_acc_ip_fecha'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(codigo_respuesta__isnull=True) | 
                      models.Q(codigo_respuesta__gte=100, codigo_respuesta__lt=600),
                name='operaciones_acceso_resp_valid'
            ),
        ]
    
    def __str__(self):
        status = "✓" if self.exitoso else "✗"
        user = self.usuario_objetivo or self.usuario_responsable
        return f"{status} {self.get_accion_display()} - {user.username} - {self.fecha_auditoria.strftime('%Y-%m-%d %H:%M')}"
    
    def get_checksum_data(self):
        return {
            'accion': self.accion,
            'objetivo_id': self.usuario_objetivo_id if self.usuario_objetivo_id else 0,
            'exitoso': self.exitoso,
            'riesgo': self.nivel_riesgo
        }

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
