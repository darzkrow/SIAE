# ============================================================================
# NUEVOS MODELOS ORGANIZACIONALES - HIDROVEN
# ============================================================================

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from auditoria.models import SoftDeleteModel

User = get_user_model()

class Empresa(SoftDeleteModel):
    """
    Modelo para la empresa principal (Hidroven).
    Representa el nivel más alto de la jerarquía organizacional.
    """
    nombre = models.CharField(
        max_length=200, 
        unique=True,
        default='Hidroven',
        help_text='Nombre de la empresa'
    )
    rif = models.CharField(
        max_length=30, 
        unique=True,
        verbose_name='RIF',
        help_text='Registro de Información Fiscal'
    )
    presidente = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='empresa_presidida',
        help_text='Presidente de la empresa (máxima autoridad)'
    )
    direccion = models.TextField(blank=True, help_text='Dirección principal')
    telefono = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    fecha_fundacion = models.DateField(null=True, blank=True)
    activa = models.BooleanField(default=True)
    
    # Campos de auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='empresas_creadas',
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def clean(self):
        """Validaciones personalizadas"""
        if self.presidente and hasattr(self.presidente, 'empresa_presidida'):
            if self.presidente.empresa_presidida.exists() and self.presidente.empresa_presidida.first() != self:
                raise ValidationError('Este usuario ya es presidente de otra empresa')


class Vicepresidencia(SoftDeleteModel):
    """
    Modelo para las vicepresidencias de Hidroven.
    Segundo nivel de la jerarquía organizacional.
    """
    class TipoVicepresidencia(models.TextChoices):
        COMERCIALIZACION = 'COMERCIALIZACION', 'Vicepresidencia de Comercialización'
        OPERACIONES = 'OPERACIONES', 'Vicepresidencia de Operaciones Hídricas'
        ADMINISTRATIVA = 'ADMINISTRATIVA', 'Vicepresidencia Administrativa'

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='vicepresidencias',
        help_text='Empresa a la que pertenece'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoVicepresidencia.choices,
        help_text='Tipo de vicepresidencia'
    )
    nombre = models.CharField(
        max_length=200,
        help_text='Nombre completo de la vicepresidencia'
    )
    codigo = models.CharField(
        max_length=10,
        unique=True,
        help_text='Código identificador (ej: VP-COM, VP-OPE, VP-ADM)'
    )
    vicepresidente = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='vicepresidencia_dirigida',
        help_text='Vicepresidente responsable'
    )
    descripcion = models.TextField(
        blank=True,
        help_text='Descripción de las funciones y responsabilidades'
    )
    activa = models.BooleanField(default=True)
    
    # Campos de auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='vicepresidencias_creadas',
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Vicepresidencia'
        verbose_name_plural = 'Vicepresidencias'
        unique_together = [
            ('empresa', 'tipo'),  # Solo una VP de cada tipo por empresa
            ('empresa', 'codigo')  # Códigos únicos por empresa
        ]
        ordering = ['empresa', 'tipo']

    def __str__(self):
        return f"{self.nombre} - {self.empresa.nombre}"

    def clean(self):
        """Validaciones personalizadas"""
        # Auto-generar nombre si no se proporciona
        if not self.nombre:
            self.nombre = self.get_tipo_display()
        
        # Auto-generar código si no se proporciona
        if not self.codigo:
            codigo_map = {
                'COMERCIALIZACION': 'VP-COM',
                'OPERACIONES': 'VP-OPE',
                'ADMINISTRATIVA': 'VP-ADM'
            }
            self.codigo = codigo_map.get(self.tipo, f'VP-{self.tipo[:3]}')

    @property
    def total_unidades(self):
        """Retorna el total de unidades organizacionales bajo esta VP"""
        return self.unidades_organizacionales.filter(activa=True).count()

    @property
    def total_acueductos(self):
        """Retorna el total de acueductos bajo esta VP"""
        return sum(unidad.acueductos.filter(activo=True).count() 
                  for unidad in self.unidades_organizacionales.filter(activa=True))


class UnidadOrganizacional(SoftDeleteModel):
    """
    Modelo genérico para unidades organizacionales bajo las vicepresidencias.
    Puede representar direcciones, gerencias, coordinaciones, almacenes regionales, etc.
    Tercer nivel de la jerarquía organizacional.
    """
    class TipoUnidad(models.TextChoices):
        DIRECCION = 'DIRECCION', 'Dirección'
        GERENCIA = 'GERENCIA', 'Gerencia'
        COORDINACION = 'COORDINACION', 'Coordinación'
        DEPARTAMENTO = 'DEPARTAMENTO', 'Departamento'
        DIVISION = 'DIVISION', 'División'
        OFICINA = 'OFICINA', 'Oficina'
        ALMACEN_REGIONAL = 'ALMACEN_REGIONAL', 'Almacén Regional'

    vicepresidencia = models.ForeignKey(
        Vicepresidencia,
        on_delete=models.CASCADE,
        related_name='unidades_organizacionales',
        help_text='Vicepresidencia a la que pertenece'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoUnidad.choices,
        help_text='Tipo de unidad organizacional'
    )
    nombre = models.CharField(
        max_length=200,
        help_text='Nombre de la unidad organizacional'
    )
    codigo = models.CharField(
        max_length=20,
        help_text='Código identificador único'
    )
    responsable = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='unidades_dirigidas',
        help_text='Responsable de la unidad (Director, Gerente, etc.)'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_unidades',
        help_text='Unidad organizacional superior (para jerarquías internas)'
    )
    descripcion = models.TextField(
        blank=True,
        help_text='Descripción de funciones y responsabilidades'
    )
    direccion = models.TextField(blank=True, help_text='Dirección física')
    telefono = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    activa = models.BooleanField(default=True)
    
    # Campos de auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='unidades_creadas',
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Unidad Organizacional'
        verbose_name_plural = 'Unidades Organizacionales'
        unique_together = [
            ('vicepresidencia', 'codigo')  # Códigos únicos por VP
        ]
        ordering = ['vicepresidencia', 'tipo', 'nombre']

    def __str__(self):
        return f"{self.get_tipo_display()} {self.nombre} - {self.vicepresidencia.codigo}"

    def clean(self):
        """Validaciones personalizadas"""
        # Validar que parent pertenezca a la misma VP
        if self.parent and self.parent.vicepresidencia != self.vicepresidencia:
            raise ValidationError('La unidad superior debe pertenecer a la misma vicepresidencia')
        
        # Evitar referencias circulares
        if self.parent == self:
            raise ValidationError('Una unidad no puede ser superior de sí misma')

    @property
    def nivel_jerarquico(self):
        """Calcula el nivel jerárquico de la unidad"""
        nivel = 1
        parent = self.parent
        while parent:
            nivel += 1
            parent = parent.parent
        return nivel

    @property
    def ruta_jerarquica(self):
        """Retorna la ruta jerárquica completa"""
        ruta = [self.nombre]
        parent = self.parent
        while parent:
            ruta.insert(0, parent.nombre)
            parent = parent.parent
        return ' > '.join(ruta)


class AcueductoNuevo(SoftDeleteModel):
    """
    Modelo actualizado para acueductos con nueva jerarquía organizacional.
    Cuarto nivel de la jerarquía organizacional.
    """
    class TipoSistema(models.TextChoices):
        ACUEDUCTO = 'ACUEDUCTO', 'Acueducto'
        PLANTA_TRATAMIENTO = 'PLANTA', 'Planta de Tratamiento'
        SISTEMA_BOMBEO = 'BOMBEO', 'Sistema de Bombeo'
        EMBALSE = 'EMBALSE', 'Embalse'
        POZO = 'POZO', 'Pozo'

    unidad_organizacional = models.ForeignKey(
        UnidadOrganizacional,
        on_delete=models.CASCADE,
        related_name='acueductos',
        help_text='Unidad organizacional responsable'
    )
    tipo_sistema = models.CharField(
        max_length=20,
        choices=TipoSistema.choices,
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
    
    # Campos de auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='acueductos_creados',
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Acueducto'
        verbose_name_plural = 'Acueductos'
        unique_together = [
            ('unidad_organizacional', 'codigo')  # Códigos únicos por unidad
        ]
        ordering = ['unidad_organizacional', 'nombre']

    def __str__(self):
        return f"{self.nombre} - {self.unidad_organizacional.codigo}"

    @property
    def vicepresidencia(self):
        """Retorna la vicepresidencia a la que pertenece"""
        return self.unidad_organizacional.vicepresidencia

    @property
    def empresa(self):
        """Retorna la empresa a la que pertenece"""
        return self.unidad_organizacional.vicepresidencia.empresa

    @property
    def ruta_organizacional_completa(self):
        """Retorna la ruta organizacional completa"""
        return f"{self.empresa.nombre} > {self.vicepresidencia.nombre} > {self.unidad_organizacional.ruta_jerarquica} > {self.nombre}"


# ============================================================================
# MODELO DE TRANSICIÓN PARA COMPATIBILIDAD
# ============================================================================

class MigracionOrganizacional(models.Model):
    """
    Modelo para mapear la estructura antigua con la nueva durante la migración.
    Permite mantener trazabilidad y rollback si es necesario.
    """
    # Referencia al modelo antiguo
    organizacion_central_antigua = models.ForeignKey(
        'institucion.OrganizacionCentral',
        on_delete=models.CASCADE,
        related_name='migraciones'
    )
    sucursal_antigua = models.ForeignKey(
        'institucion.Sucursal',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='migraciones'
    )
    acueducto_antiguo = models.ForeignKey(
        'institucion.Acueducto',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='migraciones'
    )
    
    # Referencias a los nuevos modelos
    empresa_nueva = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='migraciones'
    )
    vicepresidencia_nueva = models.ForeignKey(
        Vicepresidencia,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='migraciones'
    )
    unidad_organizacional_nueva = models.ForeignKey(
        UnidadOrganizacional,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='migraciones'
    )
    acueducto_nuevo = models.ForeignKey(
        AcueductoNuevo,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='migraciones'
    )
    
    # Metadatos de migración
    fecha_migracion = models.DateTimeField(auto_now_add=True)
    migrado_por = models.ForeignKey(User, on_delete=models.PROTECT)
    notas = models.TextField(blank=True)
    exitosa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Migración Organizacional'
        verbose_name_plural = 'Migraciones Organizacionales'
        ordering = ['-fecha_migracion']

    def __str__(self):
        return f"Migración {self.organizacion_central_antigua.nombre} -> {self.empresa_nueva.nombre if self.empresa_nueva else 'N/A'}"


# ============================================================================
# MODELOS DE TRAZABILIDAD Y ALMACENES REGIONALES
# ============================================================================

class AlmacenRegional(SoftDeleteModel):
    """
    Almacenes regionales bajo la Vicepresidencia de Operaciones Hídricas.
    Cada almacén tiene un prefijo único para la codificación de activos.
    """
    
    class EstadoVenezuela(models.TextChoices):
        ZULIA = 'ZULIA', 'Zulia'
        CARABOBO = 'CARABOBO', 'Carabobo'
        MIRANDA = 'MIRANDA', 'Miranda'
        ARAGUA = 'ARAGUA', 'Aragua'
        LARA = 'LARA', 'Lara'
        TACHIRA = 'TACHIRA', 'Táchira'
        BOLIVAR = 'BOLIVAR', 'Bolívar'
        ANZOATEGUI = 'ANZOATEGUI', 'Anzoátegui'
        MONAGAS = 'MONAGAS', 'Monagas'
    
    # Relación con la estructura organizacional
    unidad_organizacional = models.OneToOneField(
        UnidadOrganizacional,
        on_delete=models.CASCADE,
        limit_choices_to={'tipo': 'ALMACEN_REGIONAL'},
        related_name='almacen_regional'
    )
    
    # Información geográfica
    estado = models.CharField(
        max_length=20, 
        choices=EstadoVenezuela.choices,
        help_text='Estado donde se ubica el almacén'
    )
    prefijo = models.CharField(
        max_length=3, 
        unique=True,
        help_text='Prefijo único para códigos de activos (ej: ZUL, CAR, MIR)'
    )
    
    # Información operativa
    capacidad_maxima = models.PositiveIntegerField(
        help_text='Capacidad máxima de almacenamiento (número de activos)'
    )
    area_total_m2 = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True, 
        blank=True,
        help_text='Área total del almacén en metros cuadrados'
    )
    
    # Información de contacto
    telefono_principal = models.CharField(max_length=50, blank=True)
    telefono_emergencia = models.CharField(max_length=50, blank=True)
    email_almacen = models.EmailField(blank=True)
    
    # Configuración de códigos
    ultimo_secuencial = models.PositiveIntegerField(
        default=0,
        help_text='Último número secuencial usado para códigos de activos'
    )
    
    # Estado operativo
    operativo = models.BooleanField(
        default=True,
        help_text='Indica si el almacén está operativo'
    )
    fecha_apertura = models.DateField(null=True, blank=True)
    
    # Campos de auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='almacenes_creados',
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Almacén Regional'
        verbose_name_plural = 'Almacenes Regionales'
        ordering = ['estado', 'prefijo']

    def __str__(self):
        return f"Almacén {self.estado} ({self.prefijo})"

    def clean(self):
        """Validaciones personalizadas"""
        # Mapeo automático de prefijos por estado
        prefijos_por_estado = {
            'ZULIA': 'ZUL',
            'CARABOBO': 'CAR',
            'MIRANDA': 'MIR',
            'ARAGUA': 'ARA',
            'LARA': 'LAR',
            'TACHIRA': 'TAC',
            'BOLIVAR': 'BOL',
            'ANZOATEGUI': 'ANZ',
            'MONAGAS': 'MON'
        }
        
        if not self.prefijo and self.estado:
            self.prefijo = prefijos_por_estado.get(self.estado, self.estado[:3])

    @property
    def responsable(self):
        """Retorna el responsable del almacén desde la unidad organizacional"""
        return self.unidad_organizacional.responsable

    @property
    def activos_totales(self):
        """Retorna el total de activos en el almacén"""
        return self.activos_actuales.filter(estado_actual__in=['EN_ALMACEN', 'EN_TRANSITO']).count()

    @property
    def capacidad_disponible(self):
        """Retorna la capacidad disponible del almacén"""
        return self.capacidad_maxima - self.activos_totales

    @property
    def porcentaje_ocupacion(self):
        """Retorna el porcentaje de ocupación del almacén"""
        if self.capacidad_maxima == 0:
            return 0
        return (self.activos_totales / self.capacidad_maxima) * 100

    def obtener_siguiente_secuencial(self):
        """Obtiene el siguiente número secuencial para códigos de activos"""
        self.ultimo_secuencial += 1
        self.save(update_fields=['ultimo_secuencial'])
        return self.ultimo_secuencial


class ActivoInventario(SoftDeleteModel):
    """
    Modelo para cada producto individual con código único y trazabilidad completa.
    Cada activo tiene un código único que evoluciona con los traslados.
    """
    
    class TipoActivo(models.TextChoices):
        BOMBA = 'BOMBA', 'Bomba'
        MOTOR = 'MOTOR', 'Motor'
        TUBERIA = 'TUBERIA', 'Tubería'
        QUIMICO = 'QUIMICO', 'Químico'
        ACCESORIO = 'ACCESORIO', 'Accesorio'
        EQUIPO = 'EQUIPO', 'Equipo'
    
    class EstadoActivo(models.TextChoices):
        EN_ALMACEN = 'EN_ALMACEN', 'En Almacén'
        EN_TRANSITO = 'EN_TRANSITO', 'En Tránsito'
        INSTALADO = 'INSTALADO', 'Instalado'
        EN_USO = 'EN_USO', 'En Uso'
        MANTENIMIENTO = 'MANTENIMIENTO', 'En Mantenimiento'
        DADO_BAJA = 'DADO_BAJA', 'Dado de Baja'
        PERDIDO = 'PERDIDO', 'Perdido'
    
    # Código único del activo (evoluciona con traslados)
    codigo_activo = models.CharField(
        max_length=100, 
        unique=True,
        help_text='Código único del activo que evoluciona con traslados'
    )
    codigo_original = models.CharField(
        max_length=50,
        help_text='Código original sin prefijos adicionales'
    )
    
    # Información del producto base
    tipo_activo = models.CharField(max_length=20, choices=TipoActivo.choices)
    
    # Relación genérica con el producto base (Pipe, PumpAndMotor, etc.)
    producto_referencia = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE,
        help_text='Tipo de producto (Pipe, PumpAndMotor, ChemicalProduct, etc.)'
    )
    producto_id = models.PositiveIntegerField(help_text='ID del producto específico')
    producto = GenericForeignKey('producto_referencia', 'producto_id')
    
    # Ubicación y estado actual
    almacen_actual = models.ForeignKey(
        AlmacenRegional,
        on_delete=models.PROTECT,
        related_name='activos_actuales',
        help_text='Almacén donde se encuentra actualmente'
    )
    estado_actual = models.CharField(
        max_length=20, 
        choices=EstadoActivo.choices,
        default='EN_ALMACEN'
    )
    ubicacion_especifica = models.CharField(
        max_length=200, 
        blank=True,
        help_text='Ubicación específica dentro del almacén (estante, zona, etc.)'
    )
    
    # Información de origen
    almacen_origen = models.ForeignKey(
        AlmacenRegional,
        on_delete=models.PROTECT,
        related_name='activos_originados',
        help_text='Almacén donde ingresó originalmente al sistema'
    )
    fecha_ingreso_sistema = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de ingreso al sistema de trazabilidad'
    )
    
    # Información técnica del activo
    numero_serie = models.CharField(max_length=100, blank=True)
    numero_lote = models.CharField(max_length=100, blank=True)
    fecha_fabricacion = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField(
        null=True, 
        blank=True,
        help_text='Para productos químicos o con fecha de caducidad'
    )
    
    # Información financiera
    valor_unitario = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text='Valor unitario del activo'
    )
    proveedor_original = models.CharField(
        max_length=200, 
        blank=True,
        help_text='Proveedor original del activo'
    )
    
    # Información de instalación (si aplica)
    acueducto_instalado = models.ForeignKey(
        'AcueductoNuevo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activos_instalados',
        help_text='Acueducto donde está instalado (si aplica)'
    )
    fecha_instalacion = models.DateTimeField(null=True, blank=True)
    instalado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activos_instalados',
        help_text='Usuario que realizó la instalación'
    )
    
    # Campos de auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='activos_creados',
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Activo de Inventario'
        verbose_name_plural = 'Activos de Inventario'
        ordering = ['-fecha_ingreso_sistema']
        indexes = [
            models.Index(fields=['codigo_activo']),
            models.Index(fields=['codigo_original']),
            models.Index(fields=['almacen_actual', 'estado_actual']),
            models.Index(fields=['tipo_activo', 'estado_actual']),
        ]

    def __str__(self):
        return f"{self.codigo_activo} - {self.get_tipo_activo_display()}"

    def save(self, *args, **kwargs):
        """Override save para generar código automáticamente"""
        if not self.codigo_activo:
            self.codigo_activo = self.generar_codigo_activo()
            self.codigo_original = self.codigo_activo
        super().save(*args, **kwargs)

    def generar_codigo_activo(self):
        """Genera código único del activo"""
        from django.utils import timezone
        
        año = timezone.now().year
        secuencial = self.almacen_origen.obtener_siguiente_secuencial()
        return f"{self.almacen_origen.prefijo}-{self.tipo_activo}-{secuencial:06d}-{año}"

    def actualizar_codigo_por_traslado(self, nuevo_almacen):
        """Actualiza código al trasladar a nuevo almacén"""
        if nuevo_almacen != self.almacen_actual:
            # Agregar prefijo del nuevo almacén al código existente
            self.codigo_activo = f"{nuevo_almacen.prefijo}-{self.codigo_activo}"
            return self.codigo_activo
        return self.codigo_activo

    @property
    def historial_completo(self):
        """Retorna el historial completo de movimientos"""
        return self.historial_movimientos.all().order_by('-fecha_movimiento')

    @property
    def ubicacion_completa(self):
        """Retorna la ubicación completa del activo"""
        ubicacion = f"{self.almacen_actual.estado}"
        if self.ubicacion_especifica:
            ubicacion += f" - {self.ubicacion_especifica}"
        if self.acueducto_instalado:
            ubicacion += f" - {self.acueducto_instalado.nombre}"
        return ubicacion

    @property
    def dias_en_sistema(self):
        """Retorna los días que lleva el activo en el sistema"""
        from django.utils import timezone
        return (timezone.now().date() - self.fecha_ingreso_sistema.date()).days

    @property
    def numero_traslados(self):
        """Retorna el número de traslados realizados"""
        return self.historial_movimientos.filter(tipo_movimiento='TRASLADO_ALMACEN').count()


class HistorialMovimientoActivo(models.Model):
    """
    Historial completo de movimientos de cada activo.
    Registra todos los cambios de ubicación, estado y responsables.
    """
    
    class TipoMovimiento(models.TextChoices):
        INGRESO_INICIAL = 'INGRESO_INICIAL', 'Ingreso Inicial'
        TRASLADO_ALMACEN = 'TRASLADO_ALMACEN', 'Traslado entre Almacenes'
        INSTALACION = 'INSTALACION', 'Instalación en Campo'
        RETIRO_CAMPO = 'RETIRO_CAMPO', 'Retiro de Campo'
        MANTENIMIENTO_ENTRADA = 'MANTENIMIENTO_ENTRADA', 'Entrada a Mantenimiento'
        MANTENIMIENTO_SALIDA = 'MANTENIMIENTO_SALIDA', 'Salida de Mantenimiento'
        BAJA_DEFINITIVA = 'BAJA_DEFINITIVA', 'Baja Definitiva'
        REPORTE_PERDIDA = 'REPORTE_PERDIDA', 'Reporte de Pérdida'
        RECUPERACION = 'RECUPERACION', 'Recuperación de Activo'
    
    # Relación con el activo
    activo = models.ForeignKey(
        ActivoInventario,
        on_delete=models.CASCADE,
        related_name='historial_movimientos'
    )
    
    # Información del movimiento
    tipo_movimiento = models.CharField(max_length=30, choices=TipoMovimiento.choices)
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    numero_movimiento = models.CharField(
        max_length=20,
        unique=True,
        help_text='Número único del movimiento'
    )
    
    # Ubicaciones
    almacen_origen = models.ForeignKey(
        AlmacenRegional,
        on_delete=models.PROTECT,
        related_name='movimientos_origen',
        null=True, blank=True
    )
    almacen_destino = models.ForeignKey(
        AlmacenRegional,
        on_delete=models.PROTECT,
        related_name='movimientos_destino',
        null=True, blank=True
    )
    ubicacion_especifica_origen = models.CharField(max_length=200, blank=True)
    ubicacion_especifica_destino = models.CharField(max_length=200, blank=True)
    
    # Acueductos (para instalaciones)
    acueducto_origen = models.ForeignKey(
        'AcueductoNuevo',
        on_delete=models.SET_NULL,
        related_name='movimientos_origen',
        null=True, blank=True
    )
    acueducto_destino = models.ForeignKey(
        'AcueductoNuevo',
        on_delete=models.SET_NULL,
        related_name='movimientos_destino',
        null=True, blank=True
    )
    
    # Responsables del movimiento
    solicitado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='movimientos_solicitados'
    )
    aprobado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='movimientos_aprobados',
        null=True, blank=True
    )
    ejecutado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='movimientos_ejecutados',
        null=True, blank=True
    )
    recibido_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='movimientos_recibidos',
        null=True, blank=True
    )
    
    # Estados del movimiento
    estado_anterior = models.CharField(max_length=20)
    estado_nuevo = models.CharField(max_length=20)
    codigo_anterior = models.CharField(max_length=100)
    codigo_nuevo = models.CharField(max_length=100)
    
    # Información adicional
    motivo = models.TextField(help_text='Motivo del movimiento')
    observaciones = models.TextField(blank=True)
    documentos_adjuntos = models.JSONField(
        default=list, 
        blank=True,
        help_text='Lista de documentos adjuntos (URLs o referencias)'
    )
    
    # Metadatos de aprobación y ejecución
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    fecha_ejecucion = models.DateTimeField(null=True, blank=True)
    fecha_recepcion = models.DateTimeField(null=True, blank=True)
    
    # Información de transporte (si aplica)
    vehiculo_transporte = models.CharField(max_length=100, blank=True)
    conductor = models.CharField(max_length=200, blank=True)
    numero_guia = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'Historial de Movimiento'
        verbose_name_plural = 'Historial de Movimientos'
        ordering = ['-fecha_movimiento']
        indexes = [
            models.Index(fields=['activo', '-fecha_movimiento']),
            models.Index(fields=['tipo_movimiento', '-fecha_movimiento']),
            models.Index(fields=['almacen_origen', 'almacen_destino']),
        ]

    def __str__(self):
        return f"{self.activo.codigo_activo} - {self.get_tipo_movimiento_display()} - {self.fecha_movimiento.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):
        """Override save para generar número de movimiento automáticamente"""
        if not self.numero_movimiento:
            self.numero_movimiento = self.generar_numero_movimiento()
        super().save(*args, **kwargs)

    def generar_numero_movimiento(self):
        """Genera número único de movimiento"""
        from django.utils import timezone
        
        año = timezone.now().year
        mes = timezone.now().month
        dia = timezone.now().day
        
        # Contar movimientos del día
        movimientos_hoy = HistorialMovimientoActivo.objects.filter(
            fecha_movimiento__date=timezone.now().date()
        ).count() + 1
        
        return f"MOV-{año}{mes:02d}{dia:02d}-{movimientos_hoy:04d}"


class SolicitudTraslado(models.Model):
    """
    Solicitudes de traslado entre almacenes con flujo de aprobación.
    Maneja el proceso completo desde solicitud hasta confirmación.
    """
    
    class EstadoSolicitud(models.TextChoices):
        BORRADOR = 'BORRADOR', 'Borrador'
        PENDIENTE = 'PENDIENTE', 'Pendiente de Aprobación'
        APROBADA_ORIGEN = 'APROBADA_ORIGEN', 'Aprobada por Origen'
        APROBADA_DESTINO = 'APROBADA_DESTINO', 'Aprobada por Destino'
        EN_TRANSITO = 'EN_TRANSITO', 'En Tránsito'
        COMPLETADA = 'COMPLETADA', 'Completada'
        RECHAZADA = 'RECHAZADA', 'Rechazada'
        CANCELADA = 'CANCELADA', 'Cancelada'
    
    class PrioridadSolicitud(models.TextChoices):
        BAJA = 'BAJA', 'Baja'
        MEDIA = 'MEDIA', 'Media'
        ALTA = 'ALTA', 'Alta'
        URGENTE = 'URGENTE', 'Urgente'
    
    # Información básica
    numero_solicitud = models.CharField(max_length=20, unique=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20, 
        choices=EstadoSolicitud.choices, 
        default='BORRADOR'
    )
    
    # Activos a trasladar
    activos = models.ManyToManyField(
        ActivoInventario, 
        related_name='solicitudes_traslado',
        help_text='Activos incluidos en la solicitud de traslado'
    )
    
    # Almacenes
    almacen_origen = models.ForeignKey(
        AlmacenRegional,
        on_delete=models.PROTECT,
        related_name='solicitudes_origen'
    )
    almacen_destino = models.ForeignKey(
        AlmacenRegional,
        on_delete=models.PROTECT,
        related_name='solicitudes_destino'
    )
    
    # Responsables
    solicitante = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='solicitudes_realizadas'
    )
    aprobador_origen = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='aprobaciones_origen',
        null=True, blank=True
    )
    aprobador_destino = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='aprobaciones_destino',
        null=True, blank=True
    )
    
    # Información del traslado
    motivo_traslado = models.TextField()
    fecha_programada = models.DateTimeField(
        help_text='Fecha programada para el traslado'
    )
    prioridad = models.CharField(
        max_length=10,
        choices=PrioridadSolicitud.choices,
        default='MEDIA'
    )
    
    # Fechas de proceso
    fecha_aprobacion_origen = models.DateTimeField(null=True, blank=True)
    fecha_aprobacion_destino = models.DateTimeField(null=True, blank=True)
    fecha_inicio_traslado = models.DateTimeField(null=True, blank=True)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    
    # Observaciones por etapa
    observaciones_solicitante = models.TextField(blank=True)
    observaciones_origen = models.TextField(blank=True)
    observaciones_destino = models.TextField(blank=True)
    observaciones_traslado = models.TextField(blank=True)
    
    # Información de transporte
    vehiculo_asignado = models.CharField(max_length=100, blank=True)
    conductor_asignado = models.CharField(max_length=200, blank=True)
    numero_guia_transporte = models.CharField(max_length=50, blank=True)
    
    # Documentos
    documentos_adjuntos = models.JSONField(default=list, blank=True)
    
    # Campos de auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Solicitud de Traslado'
        verbose_name_plural = 'Solicitudes de Traslado'
        ordering = ['-fecha_solicitud']
        indexes = [
            models.Index(fields=['estado', '-fecha_solicitud']),
            models.Index(fields=['almacen_origen', 'almacen_destino']),
            models.Index(fields=['solicitante', '-fecha_solicitud']),
        ]

    def __str__(self):
        return f"{self.numero_solicitud} - {self.almacen_origen} → {self.almacen_destino}"

    def save(self, *args, **kwargs):
        """Override save para generar número de solicitud automáticamente"""
        if not self.numero_solicitud:
            self.numero_solicitud = self.generar_numero_solicitud()
        super().save(*args, **kwargs)

    def generar_numero_solicitud(self):
        """Genera número único de solicitud"""
        from django.utils import timezone
        
        año = timezone.now().year
        mes = timezone.now().month
        
        # Contar solicitudes del mes
        solicitudes_mes = SolicitudTraslado.objects.filter(
            fecha_solicitud__year=año,
            fecha_solicitud__month=mes
        ).count() + 1
        
        return f"ST-{año}{mes:02d}-{solicitudes_mes:04d}"

    @property
    def total_activos(self):
        """Retorna el total de activos en la solicitud"""
        return self.activos.count()

    @property
    def valor_total_traslado(self):
        """Retorna el valor total de los activos a trasladar"""
        from django.db.models import Sum
        return self.activos.aggregate(
            total=Sum('valor_unitario')
        )['total'] or 0

    @property
    def puede_aprobar_origen(self):
        """Indica si la solicitud puede ser aprobada por el origen"""
        return self.estado in ['PENDIENTE']

    @property
    def puede_aprobar_destino(self):
        """Indica si la solicitud puede ser aprobada por el destino"""
        return self.estado in ['APROBADA_ORIGEN']

    @property
    def puede_ejecutar(self):
        """Indica si la solicitud puede ser ejecutada"""
        return self.estado in ['APROBADA_DESTINO']

    def aprobar_origen(self, aprobador, observaciones=''):
        """Aprueba la solicitud desde el almacén origen"""
        if not self.puede_aprobar_origen:
            raise ValidationError('La solicitud no puede ser aprobada por el origen en su estado actual')
        
        self.aprobador_origen = aprobador
        self.fecha_aprobacion_origen = timezone.now()
        self.observaciones_origen = observaciones
        self.estado = 'APROBADA_ORIGEN'
        self.save()

    def aprobar_destino(self, aprobador, observaciones=''):
        """Aprueba la solicitud desde el almacén destino"""
        if not self.puede_aprobar_destino:
            raise ValidationError('La solicitud no puede ser aprobada por el destino en su estado actual')
        
        self.aprobador_destino = aprobador
        self.fecha_aprobacion_destino = timezone.now()
        self.observaciones_destino = observaciones
        self.estado = 'APROBADA_DESTINO'
        self.save()

    def ejecutar_traslado(self, ejecutor):
        """Ejecuta el traslado de activos"""
        if not self.puede_ejecutar:
            raise ValidationError('La solicitud no puede ser ejecutada en su estado actual')
        
        from django.utils import timezone
        
        # Cambiar estado de la solicitud
        self.estado = 'EN_TRANSITO'
        self.fecha_inicio_traslado = timezone.now()
        self.save()
        
        # Procesar cada activo
        for activo in self.activos.all():
            # Actualizar código del activo
            codigo_anterior = activo.codigo_activo
            nuevo_codigo = activo.actualizar_codigo_por_traslado(self.almacen_destino)
            
            # Cambiar estado del activo
            activo.estado_actual = 'EN_TRANSITO'
            activo.save()
            
            # Crear registro en historial
            HistorialMovimientoActivo.objects.create(
                activo=activo,
                tipo_movimiento='TRASLADO_ALMACEN',
                almacen_origen=self.almacen_origen,
                almacen_destino=self.almacen_destino,
                solicitado_por=self.solicitante,
                aprobado_por=self.aprobador_origen,
                ejecutado_por=ejecutor,
                estado_anterior='EN_ALMACEN',
                estado_nuevo='EN_TRANSITO',
                codigo_anterior=codigo_anterior,
                codigo_nuevo=nuevo_codigo,
                motivo=self.motivo_traslado,
                observaciones=f"Solicitud: {self.numero_solicitud}",
                vehiculo_transporte=self.vehiculo_asignado,
                conductor=self.conductor_asignado,
                numero_guia=self.numero_guia_transporte
            )

    def confirmar_recepcion(self, receptor):
        """Confirma la recepción de activos en el almacén destino"""
        if self.estado != 'EN_TRANSITO':
            raise ValidationError('Solo se pueden confirmar recepciones de traslados en tránsito')
        
        from django.utils import timezone
        
        # Actualizar solicitud
        self.estado = 'COMPLETADA'
        self.fecha_completada = timezone.now()
        self.save()
        
        # Actualizar activos
        for activo in self.activos.all():
            activo.almacen_actual = self.almacen_destino
            activo.estado_actual = 'EN_ALMACEN'
            activo.save()
            
            # Actualizar último movimiento
            ultimo_movimiento = activo.historial_movimientos.filter(
                tipo_movimiento='TRASLADO_ALMACEN'
            ).first()
            
            if ultimo_movimiento:
                ultimo_movimiento.recibido_por = receptor
                ultimo_movimiento.fecha_recepcion = timezone.now()
                ultimo_movimiento.save()