"""
Flota Models - Fleet Management Module

Comprehensive vehicle fleet management for all vehicle types:
motorcycles, cars, trucks, buses, boats, and heavy machinery.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import TimeStampedModel
import qrcode
from io import BytesIO
from django.core.files import File
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


# =============================================================================
# CATÁLOGO DE TIPOS DE VEHÍCULOS
# =============================================================================

class TipoVehiculo(TimeStampedModel):
    """
    Catálogo de tipos de vehículos.
    
    Categorías principales:
    - Motocicletas
    - Vehículos livianos (carros, SUV, pickups)
    - Vehículos pesados (camiones, tractores)
    - Transporte de personal (buses, minibuses)
    - Embarcaciones (lanchas, barcos, remolcadores)
    - Maquinaria (retroexcavadoras, grúas, compresores)
    """
    
    CATEGORIAS = [
        ('MOTO', 'Motocicleta'),
        ('LIVIANO', 'Vehículo Liviano'),
        ('PESADO', 'Vehículo Pesado'),
        ('TRANSPORTE', 'Transporte de Personal'),
        ('EMBARCACION', 'Embarcación'),
        ('MAQUINARIA', 'Maquinaria Pesada'),
        ('ESPECIAL', 'Vehículo Especial'),
    ]
    
    nombre = models.CharField(
        max_length=100,
        unique=True,
        help_text='Nombre del tipo de vehículo (ej: Pickup Doble Cabina)'
    )
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIAS,
        help_text='Categoría general del vehículo'
    )
    codigo = models.CharField(
        max_length=10,
        unique=True,
        help_text='Código corto para identificación (ej: PICK, MOTO, LANC)'
    )
    descripcion = models.TextField(
        blank=True,
        help_text='Descripción detallada del tipo'
    )
    
    # Requisitos especiales
    requiere_licencia_especial = models.BooleanField(
        default=False,
        help_text='Si requiere licencia especial para operar'
    )
    tipo_licencia_requerida = models.CharField(
        max_length=50,
        blank=True,
        help_text='Tipo de licencia requerida (ej: 5ta, Náutica)'
    )
    
    # Medición
    usa_kilometraje = models.BooleanField(
        default=True,
        help_text='Si el vehículo mide uso por kilómetros'
    )
    usa_horas_motor = models.BooleanField(
        default=False,
        help_text='Si el vehículo mide uso por horas de motor (embarcaciones, maquinaria)'
    )
    
    # Mantenimiento automático
    km_mantenimiento_preventivo = models.PositiveIntegerField(
        default=5000,
        help_text='Kilómetros entre mantenimientos preventivos'
    )
    horas_mantenimiento_preventivo = models.PositiveIntegerField(
        default=250,
        help_text='Horas de motor entre mantenimientos preventivos'
    )
    
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Tipo de Vehículo'
        verbose_name_plural = 'Tipos de Vehículos'
        ordering = ['categoria', 'nombre']
        indexes = [
            models.Index(fields=['categoria']),
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


# =============================================================================
# MODELO PRINCIPAL DE VEHÍCULO
# =============================================================================

class Vehiculo(TimeStampedModel):
    """
    Vehículo único en el inventario de flota.
    
    Cada vehículo es un activo único con identificación,
    documentación, historial de mantenimiento y asignaciones.
    """
    
    ESTADOS = [
        ('DISPONIBLE', 'Disponible'),
        ('EN_USO', 'En Uso'),
        ('ASIGNADO', 'Asignado Permanente'),
        ('MANTENIMIENTO', 'En Mantenimiento'),
        ('REPARACION', 'En Reparación'),
        ('RESERVADO', 'Reservado'),
        ('FUERA_SERVICIO', 'Fuera de Servicio'),
        ('SINIESTRADO', 'Siniestrado'),
        ('BAJA', 'Dado de Baja'),
    ]
    
    TIPOS_COMBUSTIBLE = [
        ('GASOLINA_91', 'Gasolina 91'),
        ('GASOLINA_95', 'Gasolina 95'),
        ('DIESEL', 'Diesel'),
        ('GAS', 'Gas Natural'),
        ('ELECTRICO', 'Eléctrico'),
        ('HIBRIDO', 'Híbrido'),
        ('NA', 'No Aplica'),
    ]
    
    TRANSMISIONES = [
        ('MANUAL', 'Manual'),
        ('AUTOMATICA', 'Automática'),
        ('CVT', 'CVT'),
        ('NA', 'No Aplica'),
    ]
    
    # =========================================================================
    # IDENTIFICACIÓN ÚNICA
    # =========================================================================
    codigo = models.CharField(
        max_length=50,
        unique=True,
        help_text='Código único interno (auto-generado)'
    )
    placa = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        help_text='Placa del vehículo (puede ser nula para embarcaciones)'
    )
    serial_motor = models.CharField(
        max_length=50,
        unique=True,
        help_text='Número de serial del motor'
    )
    serial_carroceria = models.CharField(
        max_length=50,
        unique=True,
        help_text='Número de serial de carrocería/chasis'
    )
    numero_matricula = models.CharField(
        max_length=50,
        blank=True,
        help_text='Número de matrícula (para embarcaciones)'
    )
    
    # =========================================================================
    # CLASIFICACIÓN Y CARACTERÍSTICAS
    # =========================================================================
    tipo_vehiculo = models.ForeignKey(
        TipoVehiculo,
        on_delete=models.PROTECT,
        related_name='vehiculos',
        help_text='Tipo de vehículo'
    )
    marca = models.CharField(max_length=100, help_text='Marca del vehículo')
    modelo = models.CharField(max_length=100, help_text='Modelo del vehículo')
    año = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)],
        help_text='Año de fabricación'
    )
    color = models.CharField(max_length=50, help_text='Color principal')
    
    # Especificaciones técnicas
    tipo_combustible = models.CharField(
        max_length=20,
        choices=TIPOS_COMBUSTIBLE,
        default='GASOLINA_91'
    )
    transmision = models.CharField(
        max_length=20,
        choices=TRANSMISIONES,
        default='MANUAL'
    )
    capacidad_pasajeros = models.PositiveIntegerField(
        default=5,
        help_text='Número máximo de pasajeros'
    )
    capacidad_carga_kg = models.PositiveIntegerField(
        default=0,
        help_text='Capacidad de carga en kilogramos'
    )
    capacidad_tanque = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        help_text='Capacidad del tanque de combustible en litros'
    )
    
    # =========================================================================
    # UBICACIÓN Y ASIGNACIÓN
    # =========================================================================
    unidad_organizacional = models.ForeignKey(
        'institucion.UnidadOrganizacional',
        on_delete=models.PROTECT,
        related_name='vehiculos_flota',
        help_text='Unidad organizacional propietaria'
    )
    almacen_actual = models.ForeignKey(
        'institucion.AlmacenRegional',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehiculos_flota',
        help_text='Almacén donde está resguardado (si aplica)'
    )
    responsable_actual = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehiculos_asignados',
        help_text='Usuario actualmente responsable del vehículo'
    )
    ubicacion_actual = models.CharField(
        max_length=255,
        blank=True,
        help_text='Ubicación física actual del vehículo'
    )
    
    # =========================================================================
    # ESTADO Y OPERACIÓN
    # =========================================================================
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='DISPONIBLE',
        help_text='Estado actual del vehículo'
    )
    kilometraje_actual = models.PositiveIntegerField(
        default=0,
        help_text='Kilometraje actual del vehículo'
    )
    horas_motor_actual = models.PositiveIntegerField(
        default=0,
        help_text='Horas de motor actuales (para embarcaciones/maquinaria)'
    )
    
    # Último mantenimiento
    ultimo_mantenimiento_fecha = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha del último mantenimiento'
    )
    ultimo_mantenimiento_km = models.PositiveIntegerField(
        default=0,
        help_text='Kilometraje del último mantenimiento'
    )
    ultimo_mantenimiento_horas = models.PositiveIntegerField(
        default=0,
        help_text='Horas de motor del último mantenimiento'
    )
    
    # Próximo mantenimiento programado
    proximo_mantenimiento_fecha = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha programada del próximo mantenimiento'
    )
    proximo_mantenimiento_km = models.PositiveIntegerField(
        default=0,
        help_text='Kilometraje para próximo mantenimiento'
    )
    proximo_mantenimiento_horas = models.PositiveIntegerField(
        default=0,
        help_text='Horas de motor para próximo mantenimiento'
    )
    
    # =========================================================================
    # INFORMACIÓN FINANCIERA
    # =========================================================================
    valor_adquisicion = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Valor de adquisición del vehículo'
    )
    fecha_adquisicion = models.DateField(
        help_text='Fecha de adquisición'
    )
    proveedor = models.ForeignKey(
        'proveedores.Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehiculos_vendidos',
        help_text='Proveedor del vehículo'
    )
    numero_factura = models.CharField(
        max_length=100,
        blank=True,
        help_text='Número de factura de compra'
    )
    
    # =========================================================================
    # SEGUIMIENTO Y AUDITORÍA
    # =========================================================================
    observaciones = models.TextField(
        blank=True,
        help_text='Observaciones generales sobre el vehículo'
    )
    activo = models.BooleanField(
        default=True,
        help_text='Si el vehículo está activo en el sistema'
    )
    fecha_baja = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha de baja del vehículo'
    )
    motivo_baja = models.TextField(
        blank=True,
        help_text='Motivo de la baja'
    )
    
    # QR Code
    qr_code = models.ImageField(
        upload_to='flota/qr/',
        blank=True,
        help_text='Código QR para identificación rápida'
    )
    
    # Auditoría
    creado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='vehiculos_creados',
        null=True,
        help_text='Usuario que registró el vehículo'
    )
    
    class Meta:
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['placa']),
            models.Index(fields=['serial_motor']),
            models.Index(fields=['estado']),
            models.Index(fields=['tipo_vehiculo', 'estado']),
            models.Index(fields=['unidad_organizacional', 'estado']),
            models.Index(fields=['responsable_actual']),
            models.Index(fields=['activo']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                name='unique_vehiculo_codigo'
            ),
        ]
    
    def __str__(self):
        placa_str = self.placa or self.numero_matricula or 'Sin Placa'
        return f"{self.codigo} - {self.marca} {self.modelo} ({placa_str})"
    
    def clean(self):
        """Validaciones del modelo"""
        super().clean()
        
        # Validar que embarcaciones tengan matrícula
        if self.tipo_vehiculo and self.tipo_vehiculo.categoria == 'EMBARCACION':
            if not self.numero_matricula:
                raise ValidationError({
                    'numero_matricula': 'Las embarcaciones requieren número de matrícula'
                })
        
        # Validar que vehículos terrestres tengan placa (excepto maquinaria)
        if self.tipo_vehiculo and self.tipo_vehiculo.categoria not in ['EMBARCACION', 'MAQUINARIA']:
            if not self.placa:
                raise ValidationError({
                    'placa': 'Los vehículos terrestres requieren placa'
                })
    
    def save(self, *args, **kwargs):
        """Override save para generar código y QR"""
        # Generar código si no existe
        if not self.codigo:
            self.codigo = self.generate_vehicle_code()
        
        # Calcular próximo mantenimiento si no está definido
        if not self.proximo_mantenimiento_km and self.tipo_vehiculo:
            self.proximo_mantenimiento_km = (
                self.ultimo_mantenimiento_km + 
                self.tipo_vehiculo.km_mantenimiento_preventivo
            )
        
        if not self.proximo_mantenimiento_horas and self.tipo_vehiculo:
            self.proximo_mantenimiento_horas = (
                self.ultimo_mantenimiento_horas + 
                self.tipo_vehiculo.horas_mantenimiento_preventivo
            )
        
        super().save(*args, **kwargs)
        
        # Generar QR después de guardar
        if not self.qr_code:
            self.generate_qr_code()
    
    def generate_vehicle_code(self):
        """
        Genera código único para el vehículo.
        Formato: {CATEGORIA}{TIPO}-{SECUENCIAL}-{AÑO}
        Ejemplo: LIV-PICK-000001-2024
        """
        year = timezone.now().year
        tipo_code = self.tipo_vehiculo.codigo if self.tipo_vehiculo else 'XXX'
        cat_code = self.tipo_vehiculo.categoria[:3] if self.tipo_vehiculo else 'XXX'
        
        # Obtener siguiente secuencial
        last_vehicle = Vehiculo.objects.filter(
            codigo__startswith=f"{cat_code}-{tipo_code}"
        ).order_by('-codigo').first()
        
        if last_vehicle:
            try:
                last_seq = int(last_vehicle.codigo.split('-')[2])
                seq = last_seq + 1
            except (IndexError, ValueError):
                seq = 1
        else:
            seq = 1
        
        return f"{cat_code}-{tipo_code}-{seq:06d}-{year}"
    
    def generate_qr_code(self):
        """Genera código QR con información del vehículo"""
        qr_data = (
            f"SIAE-FLOTA\n"
            f"Código: {self.codigo}\n"
            f"Placa: {self.placa or 'N/A'}\n"
            f"Tipo: {self.tipo_vehiculo.nombre if self.tipo_vehiculo else 'N/A'}\n"
            f"Serial: {self.serial_carroceria}"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        filename = f'qr_vehiculo_{self.codigo}.png'
        self.qr_code.save(filename, File(buffer), save=True)
    
    def necesita_mantenimiento(self):
        """Verifica si el vehículo necesita mantenimiento"""
        if self.tipo_vehiculo.usa_kilometraje:
            if self.kilometraje_actual >= self.proximo_mantenimiento_km:
                return True
        
        if self.tipo_vehiculo.usa_horas_motor:
            if self.horas_motor_actual >= self.proximo_mantenimiento_horas:
                return True
        
        return False
    
    def km_para_mantenimiento(self):
        """Kilómetros restantes para próximo mantenimiento"""
        if not self.tipo_vehiculo.usa_kilometraje:
            return None
        return max(0, self.proximo_mantenimiento_km - self.kilometraje_actual)
    
    def horas_para_mantenimiento(self):
        """Horas restantes para próximo mantenimiento"""
        if not self.tipo_vehiculo.usa_horas_motor:
            return None
        return max(0, self.proximo_mantenimiento_horas - self.horas_motor_actual)
    
    def actualizar_kilometraje(self, nuevo_km, usuario=None):
        """Actualiza el kilometraje del vehículo"""
        if nuevo_km < self.kilometraje_actual:
            raise ValidationError('El nuevo kilometraje no puede ser menor al actual')
        
        self.kilometraje_actual = nuevo_km
        self.save()
        
        # Verificar si necesita mantenimiento
        if self.necesita_mantenimiento():
            self.crear_alerta_mantenimiento()
    
    def actualizar_horas_motor(self, nuevas_horas, usuario=None):
        """Actualiza las horas de motor del vehículo"""
        if nuevas_horas < self.horas_motor_actual:
            raise ValidationError('Las nuevas horas no pueden ser menores a las actuales')
        
        self.horas_motor_actual = nuevas_horas
        self.save()
        
        # Verificar si necesita mantenimiento
        if self.necesita_mantenimiento():
            self.crear_alerta_mantenimiento()
    
    def crear_alerta_mantenimiento(self):
        """Crea una alerta de mantenimiento pendiente"""
        # Integración con sistema de notificaciones
        try:
            from notificaciones.models import Notificacion
            Notificacion.objects.create(
                tipo='MANTENIMIENTO_VEHICULO',
                titulo=f'Mantenimiento requerido: {self.codigo}',
                mensaje=(
                    f'El vehículo {self.marca} {self.modelo} ({self.placa or self.codigo}) '
                    f'requiere mantenimiento preventivo.'
                ),
                prioridad='ALTA',
                entidad_tipo='VEHICULO',
                entidad_id=self.id
            )
        except ImportError:
            logger.warning('Sistema de notificaciones no disponible')


# =============================================================================
# DOCUMENTOS DEL VEHÍCULO
# =============================================================================

class DocumentoVehiculo(TimeStampedModel):
    """
    Documentos asociados al vehículo.
    
    Incluye certificados, seguros, permisos y otros documentos
    con seguimiento de vencimiento y alertas automáticas.
    """
    
    TIPOS_DOCUMENTO = [
        ('REGISTRO', 'Certificado de Registro'),
        ('SEGURO', 'Póliza de Seguro'),
        ('REVISION', 'Revisión Técnica'),
        ('PERMISO_CIRCULACION', 'Permiso de Circulación'),
        ('LICENCIA_OPERACION', 'Licencia de Operación'),
        ('MATRICULA', 'Certificado de Matrícula'),
        ('INSPECCION', 'Certificado de Inspección'),
        ('FUMIGACION', 'Certificado de Fumigación'),
        ('GARANTIA', 'Certificado de Garantía'),
        ('OTRO', 'Otro Documento'),
    ]
    
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name='documentos',
        help_text='Vehículo al que pertenece el documento'
    )
    tipo_documento = models.CharField(
        max_length=30,
        choices=TIPOS_DOCUMENTO,
        help_text='Tipo de documento'
    )
    nombre = models.CharField(
        max_length=200,
        help_text='Nombre o descripción del documento'
    )
    numero_documento = models.CharField(
        max_length=100,
        blank=True,
        help_text='Número o código del documento'
    )
    
    # Fechas
    fecha_emision = models.DateField(
        help_text='Fecha de emisión del documento'
    )
    fecha_vencimiento = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha de vencimiento (si aplica)'
    )
    
    # Archivo
    archivo = models.FileField(
        upload_to='flota/documentos/',
        blank=True,
        help_text='Archivo digital del documento'
    )
    
    # Alertas
    alertar_vencimiento = models.BooleanField(
        default=True,
        help_text='Generar alerta antes del vencimiento'
    )
    dias_alerta = models.PositiveIntegerField(
        default=30,
        help_text='Días antes del vencimiento para alertar'
    )
    alerta_enviada = models.BooleanField(
        default=False,
        help_text='Si ya se envió la alerta de vencimiento'
    )
    
    # Auditoría
    subido_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='documentos_vehiculo_subidos',
        help_text='Usuario que subió el documento'
    )
    observaciones = models.TextField(
        blank=True,
        help_text='Observaciones adicionales'
    )
    
    class Meta:
        verbose_name = 'Documento de Vehículo'
        verbose_name_plural = 'Documentos de Vehículos'
        ordering = ['-fecha_vencimiento']
        indexes = [
            models.Index(fields=['vehiculo', 'tipo_documento']),
            models.Index(fields=['fecha_vencimiento']),
            models.Index(fields=['alertar_vencimiento', 'alerta_enviada']),
        ]
    
    def __str__(self):
        return f"{self.vehiculo.codigo} - {self.get_tipo_documento_display()}"
    
    @property
    def esta_vencido(self):
        """Verifica si el documento está vencido"""
        if not self.fecha_vencimiento:
            return False
        return self.fecha_vencimiento < timezone.now().date()
    
    @property
    def dias_para_vencer(self):
        """Días restantes para vencer"""
        if not self.fecha_vencimiento:
            return None
        delta = self.fecha_vencimiento - timezone.now().date()
        return delta.days
    
    @property
    def requiere_alerta(self):
        """Verifica si debe enviarse alerta de vencimiento"""
        if not self.alertar_vencimiento or self.alerta_enviada:
            return False
        if not self.fecha_vencimiento:
            return False
        
        dias = self.dias_para_vencer
        return dias is not None and dias <= self.dias_alerta


# =============================================================================
# MANTENIMIENTO DE VEHÍCULOS
# =============================================================================

class MantenimientoVehiculo(TimeStampedModel):
    """
    Registro de mantenimientos realizados y programados.
    
    Incluye mantenimientos preventivos (programados) y
    correctivos (reparaciones).
    """
    
    TIPOS_MANTENIMIENTO = [
        ('PREVENTIVO', 'Mantenimiento Preventivo'),
        ('CORRECTIVO', 'Mantenimiento Correctivo'),
        ('EMERGENCIA', 'Reparación de Emergencia'),
        ('REVISION', 'Revisión General'),
        ('CAMBIO_ACEITE', 'Cambio de Aceite'),
        ('CAMBIO_FILTROS', 'Cambio de Filtros'),
        ('CAMBIO_FRENOS', 'Cambio de Frenos'),
        ('CAMBIO_NEUMATICOS', 'Cambio de Neumáticos'),
        ('REPARACION_MOTOR', 'Reparación de Motor'),
        ('REPARACION_TRANSMISION', 'Reparación de Transmisión'),
        ('ELECTRICIDAD', 'Sistema Eléctrico'),
        ('CARROCERIA', 'Reparación de Carrocería'),
        ('OTRO', 'Otro'),
    ]
    
    ESTADOS = [
        ('PROGRAMADO', 'Programado'),
        ('EN_PROCESO', 'En Proceso'),
        ('COMPLETADO', 'Completado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name='mantenimientos',
        help_text='Vehículo'
    )
    tipo_mantenimiento = models.CharField(
        max_length=30,
        choices=TIPOS_MANTENIMIENTO,
        help_text='Tipo de mantenimiento'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='PROGRAMADO'
    )
    
    # Programación
    fecha_programada = models.DateField(
        help_text='Fecha programada para el mantenimiento'
    )
    fecha_inicio = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha de inicio del mantenimiento'
    )
    fecha_fin = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha de finalización'
    )
    
    # Mediciones al momento del servicio
    kilometraje_servicio = models.PositiveIntegerField(
        default=0,
        help_text='Kilometraje al momento del servicio'
    )
    horas_motor_servicio = models.PositiveIntegerField(
        default=0,
        help_text='Horas de motor al momento del servicio'
    )
    
    # Detalles
    descripcion = models.TextField(
        help_text='Descripción del trabajo a realizar'
    )
    trabajos_realizados = models.TextField(
        blank=True,
        help_text='Detalle de trabajos realizados'
    )
    repuestos_utilizados = models.TextField(
        blank=True,
        help_text='Lista de repuestos utilizados'
    )
    
    # Costos
    costo_mano_obra = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Costo de mano de obra'
    )
    costo_repuestos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Costo de repuestos'
    )
    costo_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Costo total del mantenimiento'
    )
    
    # Proveedor del servicio
    proveedor_servicio = models.ForeignKey(
        'proveedores.Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mantenimientos_realizados',
        help_text='Proveedor/taller que realizó el mantenimiento'
    )
    numero_factura = models.CharField(
        max_length=100,
        blank=True,
        help_text='Número de factura del servicio'
    )
    
    # Responsables
    solicitado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='mantenimientos_solicitados',
        help_text='Usuario que solicitó el mantenimiento'
    )
    realizado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mantenimientos_supervisados',
        help_text='Usuario que supervisó el mantenimiento'
    )
    
    observaciones = models.TextField(
        blank=True,
        help_text='Observaciones adicionales'
    )
    
    class Meta:
        verbose_name = 'Mantenimiento de Vehículo'
        verbose_name_plural = 'Mantenimientos de Vehículos'
        ordering = ['-fecha_programada']
        indexes = [
            models.Index(fields=['vehiculo', '-fecha_programada']),
            models.Index(fields=['tipo_mantenimiento', 'estado']),
            models.Index(fields=['fecha_programada']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"{self.vehiculo.codigo} - {self.get_tipo_mantenimiento_display()} ({self.fecha_programada})"
    
    def save(self, *args, **kwargs):
        # Calcular costo total
        self.costo_total = self.costo_mano_obra + self.costo_repuestos
        
        super().save(*args, **kwargs)
        
        # Si se completa, actualizar vehículo
        if self.estado == 'COMPLETADO' and self.fecha_fin:
            self.vehiculo.ultimo_mantenimiento_fecha = self.fecha_fin.date()
            self.vehiculo.ultimo_mantenimiento_km = self.kilometraje_servicio
            self.vehiculo.ultimo_mantenimiento_horas = self.horas_motor_servicio
            
            # Calcular próximo mantenimiento
            tipo = self.vehiculo.tipo_vehiculo
            self.vehiculo.proximo_mantenimiento_km = (
                self.kilometraje_servicio + tipo.km_mantenimiento_preventivo
            )
            self.vehiculo.proximo_mantenimiento_horas = (
                self.horas_motor_servicio + tipo.horas_mantenimiento_preventivo
            )
            self.vehiculo.save()


# =============================================================================
# ASIGNACIÓN DE VEHÍCULOS
# =============================================================================

class AsignacionVehiculo(TimeStampedModel):
    """
    Historial de asignaciones de vehículos.
    
    Registra quién es responsable de cada vehículo
    en cada momento.
    """
    
    TIPOS_ASIGNACION = [
        ('PERMANENTE', 'Asignación Permanente'),
        ('TEMPORAL', 'Asignación Temporal'),
        ('COMISION', 'Comisión de Servicio'),
        ('PRESTAMO', 'Préstamo'),
    ]
    
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name='asignaciones',
        help_text='Vehículo asignado'
    )
    usuario_asignado = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='historial_vehiculos',
        help_text='Usuario al que se asigna el vehículo'
    )
    tipo_asignacion = models.CharField(
        max_length=20,
        choices=TIPOS_ASIGNACION,
        default='TEMPORAL'
    )
    
    # Destino
    unidad_destino = models.ForeignKey(
        'institucion.UnidadOrganizacional',
        on_delete=models.PROTECT,
        related_name='vehiculos_asignados',
        help_text='Unidad organizacional de destino'
    )
    
    # Período
    fecha_inicio = models.DateTimeField(
        help_text='Inicio de la asignación'
    )
    fecha_fin = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fin de la asignación'
    )
    activa = models.BooleanField(
        default=True,
        help_text='Si la asignación está activa'
    )
    
    # Kilometraje/horas
    kilometraje_inicial = models.PositiveIntegerField(
        help_text='Kilometraje al inicio de la asignación'
    )
    kilometraje_final = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Kilometraje al final de la asignación'
    )
    horas_motor_inicial = models.PositiveIntegerField(
        default=0,
        help_text='Horas de motor al inicio'
    )
    horas_motor_final = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Horas de motor al final'
    )
    
    # Detalles
    motivo = models.TextField(
        help_text='Motivo de la asignación'
    )
    observaciones = models.TextField(
        blank=True,
        help_text='Observaciones adicionales'
    )
    
    # Responsable de la asignación
    asignado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='asignaciones_vehiculos_realizadas',
        help_text='Usuario que realizó la asignación'
    )
    
    class Meta:
        verbose_name = 'Asignación de Vehículo'
        verbose_name_plural = 'Asignaciones de Vehículos'
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['vehiculo', '-fecha_inicio']),
            models.Index(fields=['usuario_asignado', 'activa']),
            models.Index(fields=['activa']),
            models.Index(fields=['fecha_inicio', 'fecha_fin']),
        ]
    
    def __str__(self):
        return f"{self.vehiculo.codigo} → {self.usuario_asignado.get_full_name()}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Actualizar vehículo si es asignación activa
        if self.activa:
            self.vehiculo.responsable_actual = self.usuario_asignado
            self.vehiculo.estado = 'ASIGNADO' if self.tipo_asignacion == 'PERMANENTE' else 'EN_USO'
            self.vehiculo.save()
    
    def finalizar_asignacion(self, km_final=None, horas_final=None, observaciones=''):
        """Finaliza la asignación actual"""
        self.activa = False
        self.fecha_fin = timezone.now()
        self.kilometraje_final = km_final or self.vehiculo.kilometraje_actual
        self.horas_motor_final = horas_final or self.vehiculo.horas_motor_actual
        if observaciones:
            self.observaciones = f"{self.observaciones}\n\nAl finalizar: {observaciones}"
        self.save()
        
        # Liberar vehículo
        self.vehiculo.responsable_actual = None
        self.vehiculo.estado = 'DISPONIBLE'
        self.vehiculo.save()
    
    @property
    def kilometros_recorridos(self):
        """Kilómetros recorridos durante la asignación"""
        if self.kilometraje_final:
            return self.kilometraje_final - self.kilometraje_inicial
        return self.vehiculo.kilometraje_actual - self.kilometraje_inicial


# =============================================================================
# REGISTRO DE COMBUSTIBLE
# =============================================================================

class RegistroCombustible(TimeStampedModel):
    """
    Control de consumo de combustible por vehículo.
    
    Permite calcular rendimiento y detectar anomalías
    en el consumo.
    """
    
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name='registros_combustible',
        help_text='Vehículo'
    )
    
    # Datos de la carga
    fecha = models.DateTimeField(
        help_text='Fecha y hora de la carga'
    )
    tipo_combustible = models.CharField(
        max_length=20,
        choices=Vehiculo.TIPOS_COMBUSTIBLE,
        help_text='Tipo de combustible'
    )
    litros = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Litros cargados'
    )
    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Costo total de la carga'
    )
    precio_por_litro = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text='Precio por litro'
    )
    
    # Medición
    kilometraje = models.PositiveIntegerField(
        help_text='Kilometraje al momento de la carga'
    )
    horas_motor = models.PositiveIntegerField(
        default=0,
        help_text='Horas de motor al momento de la carga'
    )
    tanque_lleno = models.BooleanField(
        default=True,
        help_text='Si se llenó el tanque completamente'
    )
    
    # Ubicación
    estacion_servicio = models.CharField(
        max_length=200,
        blank=True,
        help_text='Nombre o dirección de la estación de servicio'
    )
    
    # Responsable
    registrado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='combustibles_registrados',
        help_text='Usuario que registró la carga'
    )
    conductor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='cargas_combustible',
        help_text='Conductor al momento de la carga'
    )
    
    observaciones = models.TextField(
        blank=True,
        help_text='Observaciones adicionales'
    )
    
    class Meta:
        verbose_name = 'Registro de Combustible'
        verbose_name_plural = 'Registros de Combustible'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['vehiculo', '-fecha']),
            models.Index(fields=['fecha']),
            models.Index(fields=['tipo_combustible']),
        ]
    
    def __str__(self):
        return f"{self.vehiculo.codigo} - {self.litros}L ({self.fecha.strftime('%Y-%m-%d')})"
    
    def save(self, *args, **kwargs):
        # Calcular precio por litro si no está definido
        if self.litros > 0 and self.costo > 0 and not self.precio_por_litro:
            self.precio_por_litro = self.costo / self.litros
        
        super().save(*args, **kwargs)
        
        # Actualizar kilometraje del vehículo si es mayor
        if self.kilometraje > self.vehiculo.kilometraje_actual:
            self.vehiculo.kilometraje_actual = self.kilometraje
            self.vehiculo.save()
        
        if self.horas_motor > self.vehiculo.horas_motor_actual:
            self.vehiculo.horas_motor_actual = self.horas_motor
            self.vehiculo.save()
    
    @property
    def rendimiento_km_por_litro(self):
        """
        Calcula rendimiento basado en el registro anterior.
        Solo es preciso si ambos registros son con tanque lleno.
        """
        if not self.tanque_lleno or self.litros == 0:
            return None
        
        registro_anterior = RegistroCombustible.objects.filter(
            vehiculo=self.vehiculo,
            fecha__lt=self.fecha,
            tanque_lleno=True
        ).order_by('-fecha').first()
        
        if not registro_anterior:
            return None
        
        km_recorridos = self.kilometraje - registro_anterior.kilometraje
        if km_recorridos <= 0:
            return None
        
        return km_recorridos / float(self.litros)
