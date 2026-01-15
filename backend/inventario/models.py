"""
Modelos refactorizados para Sistema de Inventario de Agua Potable y Saneamiento.
Usa Abstract Base Classes para herencia óptima de rendimiento.
"""
from django.db import models, transaction
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
from decimal import Decimal
import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from institucion.models import Acueducto, Sucursal, OrganizacionCentral
from geography.models import Ubicacion
from geography.models import Ubicacion


# ============================================================================
# MODELOS AUXILIARES DEL NUEVO SISTEMA
# ============================================================================

class Category(models.Model):
    """Categorías de productos para clasificación."""
    nombre = models.CharField(max_length=150, unique=True)
    codigo = models.CharField(
        max_length=10,
        unique=True,
        help_text='Código para generar SKU (ej: QUI, TUB, BOM)'
    )
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    orden = models.IntegerField(default=0, help_text='Orden de visualización')

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['orden', 'nombre']
        indexes = [
            models.Index(fields=['activo']),
        ]

    def __str__(self):
        return self.nombre


class UnitOfMeasure(models.Model):
    """Unidades de medida normalizadas."""
    
    class TipoUnidad(models.TextChoices):
        LONGITUD = 'LONGITUD', 'Longitud'
        VOLUMEN = 'VOLUMEN', 'Volumen'
        PESO = 'PESO', 'Peso'
        UNIDAD = 'UNIDAD', 'Unidad'
        AREA = 'AREA', 'Área'

    nombre = models.CharField(max_length=50, unique=True)
    simbolo = models.CharField(max_length=10, unique=True)
    tipo = models.CharField(max_length=20, choices=TipoUnidad.choices)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'
        ordering = ['tipo', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.simbolo})"


class Supplier(models.Model):
    """Proveedores de productos."""
    nombre = models.CharField(max_length=200, unique=True)
    rif = models.CharField(max_length=30, blank=True, verbose_name='RIF')
    codigo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    contacto_nombre = models.CharField(max_length=150, blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['activo']),
        ]

    def __str__(self):
        return self.nombre


# ============================================================================
# MODELO BASE ABSTRACTO
# ============================================================================

class ProductBase(models.Model):
    """
    Modelo base abstracto para todos los productos.
    Contiene campos comunes a todos los tipos de productos.
    """
    # Identificación
    sku = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='SKU',
        help_text='Código único de producto (se genera automáticamente)'
    )
    nombre = models.CharField(max_length=250)
    descripcion = models.TextField(blank=True)
    
    # Clasificación
    categoria = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='%(class)s_productos'
    )
    unidad_medida = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.PROTECT,
        related_name='%(class)s_productos'
    )
    
    # Stock y Precio
    stock_actual = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0.000'))],
        help_text='Stock actual disponible'
    )
    stock_minimo = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0.000'))],
        help_text='Stock mínimo de seguridad'
    )
    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Precio por unidad de medida'
    )
    
    # Proveedor
    proveedor = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='%(class)s_productos'
    )
    
    # Estado y Fechas
    activo = models.BooleanField(default=True)
    fecha_entrada = models.DateField(
        default=timezone.now,
        help_text='Fecha de primera entrada al inventario'
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    # Notas
    notas = models.TextField(blank=True, help_text='Notas adicionales')

    class Meta:
        abstract = True
        ordering = ['sku']

    def __str__(self):
        return f"{self.sku} - {self.nombre}"

    def clean(self):
        """Validaciones personalizadas."""
        if self.stock_minimo > self.stock_actual:
            # Solo advertencia, no error
            pass
        
        if self.precio_unitario < 0:
            raise ValidationError('El precio unitario no puede ser negativo')

    def save(self, *args, **kwargs):
        # Generar SKU si no existe
        if not self.sku:
            self.sku = self.generate_sku()
        
        self.full_clean()
        super().save(*args, **kwargs)

    def generate_sku(self):
        """
        Genera un SKU único basado en categoría y correlativo.
        Formato: {CATEGORIA_CODE}-{TIPO}-{CORRELATIVO}
        """
        categoria_code = self.categoria.codigo if self.categoria else 'GEN'
        tipo_code = self.__class__.__name__[:3].upper()
        
        # Buscar último correlativo para esta categoría
        model_class = self.__class__
        last_product = model_class.objects.filter(
            sku__startswith=f"{categoria_code}-{tipo_code}-"
        ).order_by('-sku').first()
        
        if last_product:
            try:
                last_number = int(last_product.sku.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"{categoria_code}-{tipo_code}-{new_number:04d}"

    def get_stock_status(self):
        """
        Devuelve el estado del stock.
        Returns:
            str: 'AGOTADO', 'CRITICO', 'BAJO', 'NORMAL'
        """
        if self.stock_actual <= 0:
            return 'AGOTADO'
        elif self.stock_actual <= self.stock_minimo:
            return 'CRITICO'
        elif self.stock_actual <= self.stock_minimo * Decimal('1.5'):
            return 'BAJO'
        return 'NORMAL'

    def is_below_minimum(self):
        """Verifica si el stock está por debajo del mínimo."""
        return self.stock_actual <= self.stock_minimo

    def get_stock_percentage(self):
        """Calcula el porcentaje de stock vs mínimo."""
        if self.stock_minimo > 0:
            return float((self.stock_actual / self.stock_minimo) * 100)
        return 100.0


# ============================================================================
# MODELOS ESPECÍFICOS DE PRODUCTOS
# ============================================================================

class ChemicalProduct(ProductBase):
    """Productos químicos para tratamiento de agua."""
    
    class NivelPeligrosidad(models.TextChoices):
        BAJO = 'BAJO', 'Bajo'
        MEDIO = 'MEDIO', 'Medio'
        ALTO = 'ALTO', 'Alto'
        MUY_ALTO = 'MUY_ALTO', 'Muy Alto'
    
    class TipoPresentacion(models.TextChoices):
        SACO = 'SACO', 'Saco'
        TAMBOR = 'TAMBOR', 'Tambor/Bidón'
        GRANEL = 'GRANEL', 'Granel'
        GALON = 'GALON', 'Galón'
        CILINDRO = 'CILINDRO', 'Cilindro'
        OTRO = 'OTRO', 'Otro'
    
    class UnidadConcentracion(models.TextChoices):
        PORCENTAJE = 'PORCENTAJE', '% (Porcentaje)'
        G_L = 'G_L', 'g/L (Gramos por litro)'
        MG_L = 'MG_L', 'mg/L (Miligramos por litro)'
        PPM = 'PPM', 'ppm (Partes por millón)'

    # Seguridad
    es_peligroso = models.BooleanField(
        default=False,
        help_text='¿El producto es peligroso?'
    )
    nivel_peligrosidad = models.CharField(
        max_length=15,
        choices=NivelPeligrosidad.choices,
        blank=True
    )
    
    # Especificaciones Químicas
    fecha_caducidad = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha de vencimiento del lote actual'
    )
    concentracion = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Concentración del químico'
    )
    unidad_concentracion = models.CharField(
        max_length=20,
        choices=UnidadConcentracion.choices,
        default=UnidadConcentracion.PORCENTAJE
    )
    
    # Presentación
    presentacion = models.CharField(
        max_length=20,
        choices=TipoPresentacion.choices,
        default=TipoPresentacion.SACO
    )
    peso_neto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Peso neto por unidad en kg'
    )
    
    # Documentación
    ficha_seguridad = models.FileField(
        upload_to='fichas_seguridad/',
        null=True,
        blank=True,
        help_text='Ficha de datos de seguridad (MSDS/FDS)'
    )
    numero_un = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Número UN',
        help_text='Número de Naciones Unidas'
    )

    class Meta:
        verbose_name = 'Producto Químico'
        verbose_name_plural = 'Productos Químicos'
        indexes = [
            models.Index(fields=['es_peligroso']),
            models.Index(fields=['fecha_caducidad']),
            models.Index(fields=['presentacion']),
        ]

    def clean(self):
        super().clean()
        if self.es_peligroso and not self.nivel_peligrosidad:
            raise ValidationError(
                'Debe especificar el nivel de peligrosidad para productos peligrosos'
            )

    def is_expired(self):
        """Verifica si el producto está vencido."""
        if self.fecha_caducidad:
            return timezone.now().date() >= self.fecha_caducidad
        return False

    def days_until_expiration(self):
        """Días hasta la fecha de caducidad."""
        if self.fecha_caducidad:
            delta = self.fecha_caducidad - timezone.now().date()
            return delta.days
        return None


class Pipe(ProductBase):
    """Tuberías para sistemas de agua potable."""
    
    class Material(models.TextChoices):
        PVC = 'PVC', 'PVC (Policloruro de Vinilo)'
        PEAD = 'PEAD', 'PEAD (Polietileno Alta Densidad)'
        ACERO = 'ACERO', 'Acero Inoxidable'
        HIERRO_DUCTIL = 'HIERRO_DUCTIL', 'Hierro Dúctil'
        CEMENTO = 'CEMENTO', 'Cemento/Hormigón'
        COBRE = 'COBRE', 'Cobre'
        OTRO = 'OTRO', 'Otro'
    
    class UnidadDiametro(models.TextChoices):
        PULGADAS = 'PULGADAS', 'Pulgadas (")'
        MM = 'MM', 'Milímetros (mm)'
    
    class PresionNominal(models.TextChoices):
        PN6 = 'PN6', 'PN 6 bar'
        PN10 = 'PN10', 'PN 10 bar'
        PN16 = 'PN16', 'PN 16 bar'
        PN20 = 'PN20', 'PN 20 bar'
        PN25 = 'PN25', 'PN 25 bar'
        SDR11 = 'SDR11', 'SDR 11'
        SDR17 = 'SDR17', 'SDR 17'
        SDR21 = 'SDR21', 'SDR 21'
        SDR26 = 'SDR26', 'SDR 26'
        SDR41 = 'SDR41', 'SDR 41'
    
    class TipoUnion(models.TextChoices):
        SOLDABLE = 'SOLDABLE', 'Soldable (Cementar)'
        ROSCADA = 'ROSCADA', 'Roscada'
        BRIDADA = 'BRIDADA', 'Bridada'
        CAMPANA = 'CAMPANA', 'Espiga y Campana'
        FUSION = 'FUSION', 'Termofusión'
    
    class TipoUso(models.TextChoices):
        POTABLE = 'POTABLE', 'Agua Potable'
        SERVIDAS = 'SERVIDAS', 'Aguas Servidas'
        RIEGO = 'RIEGO', 'Riego'
        PLUVIAL = 'PLUVIAL', 'Agua Pluvial'
        INDUSTRIAL = 'INDUSTRIAL', 'Uso Industrial'

    # Especificaciones
    material = models.CharField(max_length=20, choices=Material.choices)
    diametro_nominal = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    unidad_diametro = models.CharField(
        max_length=10,
        choices=UnidadDiametro.choices,
        default=UnidadDiametro.MM
    )
    presion_nominal = models.CharField(
        max_length=10,
        choices=PresionNominal.choices
    )
    presion_psi = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Presión en PSI (calculado automáticamente)'
    )
    longitud_unitaria = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('6.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Longitud por unidad en metros'
    )
    tipo_union = models.CharField(max_length=20, choices=TipoUnion.choices)
    tipo_uso = models.CharField(max_length=20, choices=TipoUso.choices)
    
    # Especificaciones adicionales
    espesor_pared = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Espesor de pared en mm'
    )

    class Meta:
        verbose_name = 'Tubería'
        verbose_name_plural = 'Tuberías'
        indexes = [
            models.Index(fields=['material']),
            models.Index(fields=['diametro_nominal']),
            models.Index(fields=['tipo_uso']),
        ]

    def save(self, *args, **kwargs):
        # Calcular presión en PSI si está en PN
        if self.presion_nominal.startswith('PN'):
            try:
                bar = int(self.presion_nominal.replace('PN', ''))
                self.presion_psi = Decimal(str(bar * 14.5038)).quantize(Decimal('0.00'))
            except:
                pass
        super().save(*args, **kwargs)

    def get_diametro_display(self):
        """Retorna el diámetro con su unidad."""
        return f"{self.diametro_nominal} {self.get_unidad_diametro_display()}"


# Continuará en el próximo archivo...
"""
Modelos refactorizados - PARTE 2
Continúa desde models_refactored.py
"""

# Agregar al final de models_refactored.py


class PumpAndMotor(ProductBase):
    """Bombas y motores para sistemas de agua."""
    
    class TipoEquipo(models.TextChoices):
        BOMBA_CENTRIFUGA = 'BOMBA_CENTRIFUGA', 'Bomba Centrífuga'
        BOMBA_SUMERGIBLE = 'BOMBA_SUMERGIBLE', 'Bomba Sumergible'
        BOMBA_PERIFERICA = 'BOMBA_PERIFERICA', 'Bomba Periférica'
        BOMBA_TURBINA = 'BOMBA_TURBINA', 'Bomba de Turbina'
        MOTOR_ELECTRICO = 'MOTOR_ELECTRICO', 'Motor Eléctrico'
        VARIADOR_FRECUENCIA = 'VARIADOR', 'Variador de Frecuencia'
    
    class Fases(models.TextChoices):
        MONOFASICO = 'MONOFASICO', 'Monofásico'
        TRIFASICO = 'TRIFASICO', 'Trifásico'

    # Identificación
    tipo_equipo = models.CharField(max_length=30, choices=TipoEquipo.choices)
    marca = models.CharField(max_length=150)
    modelo = models.CharField(max_length=150)
    numero_serie = models.CharField(
        max_length=150,
        unique=True,
        help_text='Número de serie único del fabricante'
    )
    
    # Especificaciones Eléctricas
    potencia_hp = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Potencia (HP)',
        help_text='Potencia en caballos de fuerza'
    )
    potencia_kw = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Potencia (kW)',
        help_text='Potencia en kilovatios (calculado automáticamente)'
    )
    voltaje = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text='Voltaje nominal (ej: 110, 220, 440)'
    )
    fases = models.CharField(max_length=15, choices=Fases.choices)
    frecuencia = models.IntegerField(
        default=60,
        choices=[(50, '50 Hz'), (60, '60 Hz')],
        help_text='Frecuencia en Hertz'
    )
    amperaje = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Amperaje nominal'
    )
    
    # Especificaciones Hidráulicas (para bombas)
    caudal_maximo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Caudal máximo en L/s o m³/h'
    )
    unidad_caudal = models.CharField(
        max_length=10,
        choices=[('L/S', 'L/s'), ('M3/H', 'm³/h')],
        default='L/S'
    )
    altura_dinamica = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Altura dinámica total en metros'
    )
    eficiencia = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Eficiencia en porcentaje'
    )
    
    # Características adicionales
    npsh_requerido = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='NPSH Requerido',
        help_text='NPSH requerido en metros'
    )
    
    # Documentación
    curva_caracteristica = models.FileField(
        upload_to='curvas_bombas/',
        null=True,
        blank=True,
        help_text='Archivo con curva característica de la bomba'
    )

    class Meta:
        verbose_name = 'Bomba y Motor'
        verbose_name_plural = 'Bombas y Motores'
        indexes = [
            models.Index(fields=['tipo_equipo']),
            models.Index(fields=['potencia_hp']),
            models.Index(fields=['marca', 'modelo']),
        ]

    def save(self, *args, **kwargs):
        # Calcular potencia en kW automáticamente
        if self.potencia_hp:
            self.potencia_kw = (self.potencia_hp * Decimal('0.7457')).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)

    def get_potencia_display(self):
        """Retorna potencia en ambas unidades."""
        return f"{self.potencia_hp} HP ({self.potencia_kw:.2f} kW)"


class Accessory(ProductBase):
    """Accesorios para sistemas de tuberías (válvulas, codos, tees, etc)."""
    
    class TipoAccesorio(models.TextChoices):
        VALVULA = 'VALVULA', 'Válvula'
        CODO = 'CODO', 'Codo'
        TEE = 'TEE', 'Tee/T'
        REDUCCION = 'REDUCCION', 'Reducción'
        TAPON = 'TAPON', 'Tapón'
        BRIDA = 'BRIDA', 'Brida'
        UNION = 'UNION', 'Unión'
        COLLAR = 'COLLAR', 'Collar de Derivación'
        ADAPTADOR = 'ADAPTADOR', 'Adaptador'
    
    class SubtipoValvula(models.TextChoices):
        BOLA = 'BOLA', 'Bola'
        COMPUERTA = 'COMPUERTA', 'Compuerta'
        RETENCION = 'RETENCION', 'Retención/Check'
        MARIPOSA = 'MARIPOSA', 'Mariposa'
        GLOBO = 'GLOBO', 'Globo'
        ALIVIO = 'ALIVIO', 'Alivio de Presión'
        FLOTADOR = 'FLOTADOR', 'Flotador'
    
    class TipoConexion(models.TextChoices):
        BRIDADA = 'BRIDADA', 'Bridada'
        ROSCADA = 'ROSCADA', 'Roscada'
        SOLDABLE = 'SOLDABLE', 'Soldable'
        CAMPANA = 'CAMPANA', 'Espiga y Campana'
        RAPIDA = 'RAPIDA', 'Conexión Rápida'
    
    class Material(models.TextChoices):
        PVC = 'PVC', 'PVC'
        HIERRO = 'HIERRO', 'Hierro Fundido/Dúctil'
        ACERO = 'ACERO', 'Acero Inoxidable'
        BRONCE = 'BRONCE', 'Bronce'
        LATON = 'LATON', 'Latón'
        PLASTICO = 'PLASTICO', 'Plástico'

    # Tipo y subtipo
    tipo_accesorio = models.CharField(max_length=20, choices=TipoAccesorio.choices)
    subtipo = models.CharField(
        max_length=20,
        choices=SubtipoValvula.choices,
        blank=True,
        help_text='Aplica principalmente para válvulas'
    )
    
    # Dimensiones
    diametro_entrada = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Diámetro de entrada en pulgadas o mm'
    )
    diametro_salida = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Diámetro de salida (para reducciones)'
    )
    unidad_diametro = models.CharField(
        max_length=10,
        choices=[('PULGADAS', 'Pulgadas'), ('MM', 'mm')],
        default='PULGADAS'
    )
    
    # Especificaciones
    tipo_conexion = models.CharField(max_length=20, choices=TipoConexion.choices)
    angulo = models.IntegerField(
        null=True,
        blank=True,
        choices=[(45, '45°'), (90, '90°'), (180, '180°')],
        help_text='Ángulo (para codos)'
    )
    presion_trabajo = models.CharField(
        max_length=10,
        choices=[
            ('PN6', 'PN 6'), ('PN10', 'PN 10'), ('PN16', 'PN 16'),
            ('PN20', 'PN 20'), ('PN25', 'PN 25'),
            ('150LB', '150 LB'), ('300LB', '300 LB')
        ],
        help_text='Presión de trabajo nominal'
    )
    material = models.CharField(max_length=20, choices=Material.choices)

    class Meta:
        verbose_name = 'Accesorio'
        verbose_name_plural = 'Accesorios'
        indexes = [
            models.Index(fields=['tipo_accesorio']),
            models.Index(fields=['tipo_conexion']),
            models.Index(fields=['diametro_entrada']),
        ]

    def clean(self):
        super().clean()
        # Validar que reducciones tengan diámetro de salida
        if self.tipo_accesorio == 'REDUCCION' and not self.diametro_salida:
            raise ValidationError('Las reducciones deben especificar diámetro de salida')
        
        # Validar que codos tengan ángulo
        if self.tipo_accesorio == 'CODO' and not self.angulo:
            raise ValidationError('Los codos deben especificar el ángulo')

    def get_dimension_display(self):
        """Retorna las dimensiones formateadas."""
        entrada = f"{self.diametro_entrada} {self.unidad_diametro}"
        if self.diametro_salida:
            salida = f"{self.diametro_salida} {self.unidad_diametro}"
            return f"{entrada} x {salida}"
        return entrada


# ============================================================================
# MODELOS DE STOCK POR TIPO DE PRODUCTO
# ============================================================================

class StockChemical(models.Model):
    """Stock de productos químicos por ubicación."""
    producto = models.ForeignKey(
        ChemicalProduct,
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    ubicacion = models.ForeignKey(
        'geography.Ubicacion',
        on_delete=models.CASCADE,
        related_name='stocks_chemical'
    )
    cantidad = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0.000'))]
    )
    lote = models.CharField(max_length=50, blank=True, help_text='Número de lote')
    fecha_vencimiento = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha de vencimiento de este lote'
    )
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Stock de Químico'
        verbose_name_plural = 'Stocks de Químicos'
        unique_together = ('producto', 'ubicacion', 'lote')
        ordering = ['producto', 'ubicacion']
        indexes = [
            models.Index(fields=['producto', 'ubicacion']),
            models.Index(fields=['fecha_vencimiento']),
        ]

    def __str__(self):
        return f"{self.producto.nombre} @ {self.ubicacion}: {self.cantidad}"


class StockPipe(models.Model):
    """Stock de tuberías por ubicación."""
    producto = models.ForeignKey(
        Pipe,
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    ubicacion = models.ForeignKey(
        'geography.Ubicacion',
        on_delete=models.CASCADE,
        related_name='stocks_pipe'
    )
    cantidad = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0.000'))],
        help_text='Cantidad en unidades (tubos)'
    )
    metros_totales = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Metros lineales totales (calculado)'
    )
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Stock de Tubería'
        verbose_name_plural = 'Stocks de Tuberías'
        unique_together = ('producto', 'ubicacion')
        ordering = ['producto', 'ubicacion']
        indexes = [
            models.Index(fields=['producto', 'ubicacion']),
        ]

    def save(self, *args, **kwargs):
        # Calcular metros totales automáticamente
        if self.producto and self.cantidad:
            self.metros_totales = self.cantidad * self.producto.longitud_unitaria
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.nombre} @ {self.ubicacion}: {self.cantidad} un ({self.metros_totales}m)"


class StockPumpAndMotor(models.Model):
    """Stock de bombas y motores por ubicación."""
    producto = models.ForeignKey(
        PumpAndMotor,
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    ubicacion = models.ForeignKey(
        'geography.Ubicacion',
        on_delete=models.CASCADE,
        related_name='stocks_pump'
    )
    cantidad = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Cantidad de equipos'
    )
    estado_operativo = models.CharField(
        max_length=20,
        choices=[
            ('NUEVO', 'Nuevo'),
            ('OPERATIVO', 'Operativo'),
            ('MANTENIMIENTO', 'En Mantenimiento'),
            ('AVERIADO', 'Averiado'),
            ('BAJA', 'Dado de Baja')
        ],
        default='NUEVO'
    )
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Stock de Bomba/Motor'
        verbose_name_plural = 'Stocks de Bombas/Motores'
        unique_together = ('producto', 'ubicacion')
        ordering = ['producto', 'ubicacion']
        indexes = [
            models.Index(fields=['producto', 'ubicacion']),
            models.Index(fields=['estado_operativo']),
        ]

    def __str__(self):
        return f"{self.producto.numero_serie} @ {self.ubicacion}: {self.cantidad}"


class StockAccessory(models.Model):
    """Stock de accesorios por ubicación."""
    producto = models.ForeignKey(
        Accessory,
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    ubicacion = models.ForeignKey(
        'geography.Ubicacion',
        on_delete=models.CASCADE,
        related_name='stocks_accessory'
    )
    cantidad = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0.000'))]
    )
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Stock de Accesorio'
        verbose_name_plural = 'Stocks de Accesorios'
        unique_together = ('producto', 'ubicacion')
        ordering = ['producto', 'ubicacion']
        indexes = [
            models.Index(fields=['producto', 'ubicacion']),
        ]

    def __str__(self):
        return f"{self.producto.nombre} @ {self.ubicacion}: {self.cantidad}"


from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

# ... (existing imports)
from geography.models import Ubicacion

# ============================================================================
# AUDITORÍA Y MOVIMIENTOS
# ============================================================================

class InventoryAudit(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_SUCCESS = 'SUCCESS'
    STATUS_FAILED = 'FAILED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendiente'),
        (STATUS_SUCCESS, 'Exitoso'),
        (STATUS_FAILED, 'Fallido'),
    ]

    movimiento = models.ForeignKey(
        'MovimientoInventario',
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='audits'
    )
    # Generic relation to product
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    producto = GenericForeignKey('content_type', 'object_id')
    
    tipo_movimiento = models.CharField(max_length=20, blank=True)
    cantidad = models.DecimalField(max_digits=12, decimal_places=3, null=True)
    
    ubicacion_origen = models.ForeignKey(
        'geography.Ubicacion', on_delete=models.SET_NULL, null=True, blank=True, related_name='+'
    )
    ubicacion_destino = models.ForeignKey(
        'geography.Ubicacion', on_delete=models.SET_NULL, null=True, blank=True, related_name='+'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    mensaje = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Auditoría de Inventario'
        verbose_name_plural = 'Auditorías de Inventario'
        ordering = ['-fecha']

    def __str__(self):
        return f"[{self.status}] {self.tipo_movimiento} ({self.fecha})"


class MovimientoInventario(models.Model):
    T_ENTRADA = 'ENTRADA'
    T_SALIDA = 'SALIDA'
    T_TRANSFER = 'TRANSFERENCIA'
    T_AJUSTE = 'AJUSTE'

    TIPO_CHOICES = [
        (T_ENTRADA, 'Entrada'),
        (T_SALIDA, 'Salida'),
        (T_TRANSFER, 'Transferencia'),
        (T_AJUSTE, 'Ajuste'),
    ]

    STATUS_PENDIENTE = 'PENDIENTE'
    STATUS_APROBADO = 'APROBADO'
    STATUS_RECHAZADO = 'RECHAZADO'

    STATUS_CHOICES = [
        (STATUS_PENDIENTE, 'Pendiente'),
        (STATUS_APROBADO, 'Aprobado'),
        (STATUS_RECHAZADO, 'Rechazado'),
    ]

    # Relación Genérica al Producto
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    producto = GenericForeignKey('content_type', 'object_id')

    ubicacion_origen = models.ForeignKey(
        'geography.Ubicacion', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='movimientos_salida'
    )
    ubicacion_destino = models.ForeignKey(
        'geography.Ubicacion', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='movimientos_entrada'
    )

    tipo_movimiento = models.CharField(max_length=20, choices=TIPO_CHOICES)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default=STATUS_PENDIENTE
    )
    cantidad = models.DecimalField(
        max_digits=12, decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    razon = models.TextField(blank=True)
    
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='movimientos_creados'
    )
    aprobado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='movimientos_aprobados'
    )

    class Meta:
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-fecha_movimiento']

    def __init__(self, *args, **kwargs):
        # Compatibilidad con kwargs legacy
        acueducto_origen = kwargs.pop('acueducto_origen', None)
        acueducto_destino = kwargs.pop('acueducto_destino', None)
        
        super().__init__(*args, **kwargs)
        
        # Lógica para mapear acueducto a ubicación de almacén por defecto
        if acueducto_origen and not self.ubicacion_origen_id:
            self.ubicacion_origen, _ = Ubicacion.objects.get_or_create(
                acueducto=acueducto_origen,
                tipo=Ubicacion.TipoUbicacion.ALMACEN,
                defaults={'nombre': f'Almacén General {acueducto_origen.nombre}'}
            )
        if acueducto_destino and not self.ubicacion_destino_id:
            self.ubicacion_destino, _ = Ubicacion.objects.get_or_create(
                acueducto=acueducto_destino,
                tipo=Ubicacion.TipoUbicacion.ALMACEN,
                defaults={'nombre': f'Almacén General {acueducto_destino.nombre}'}
            )

    def __str__(self):
        return f"{self.tipo_movimiento} {self.cantidad} - {self.producto}"

    def get_stock_model(self):
        """Determina el modelo de stock basado en el producto."""
        model_name = self.content_type.model
        if model_name == 'chemicalproduct':
            return StockChemical
        elif model_name == 'pipe':
            return StockPipe
        elif model_name == 'pumpandmotor':
            return StockPumpAndMotor
        elif model_name == 'accessory':
            return StockAccessory
        raise ValidationError(f"Tipo de producto no soportado: {model_name}")

    def _update_stock(self, stock_model, ubicacion, cantidad, operacion):
        """Actualiza o crea registro de stock."""
        stock, created = stock_model.objects.get_or_create(
            producto_id=self.object_id,
            ubicacion=ubicacion,
            defaults={'cantidad': 0}
        )
        
        if operacion == 'sumar':
            stock.cantidad += cantidad
        elif operacion == 'restar':
            if stock.cantidad < cantidad:
                raise ValidationError(f"Stock insuficiente en {ubicacion}")
            stock.cantidad -= cantidad
            
        stock.save()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        if not is_new:
            old_instance = MovimientoInventario.objects.get(pk=self.pk)
            old_status = old_instance.status

        try:
            StockModel = self.get_stock_model()
        except Exception as e:
            raise e
        
        should_update_stock = (is_new and self.status == self.STATUS_APROBADO) or \
                              (not is_new and old_status == self.STATUS_PENDIENTE and self.status == self.STATUS_APROBADO)

        audit = None
        if is_new:
            audit = InventoryAudit(
                movimiento=self,
                content_type=self.content_type,
                object_id=self.object_id,
                tipo_movimiento=self.tipo_movimiento,
                cantidad=self.cantidad,
                ubicacion_origen=self.ubicacion_origen,
                ubicacion_destino=self.ubicacion_destino,
                user=self.creado_por,
                status=InventoryAudit.STATUS_PENDING
            )

        try:
            with transaction.atomic():
                super().save(*args, **kwargs)
                
                if is_new and audit:
                    audit.movimiento = self
                    audit.save()

                if should_update_stock:
                    if self.tipo_movimiento == self.T_ENTRADA:
                        if not self.ubicacion_destino:
                            raise ValidationError("Destino requerido para entrada")
                        self._update_stock(StockModel, self.ubicacion_destino, self.cantidad, 'sumar')

                    elif self.tipo_movimiento == self.T_SALIDA:
                        if not self.ubicacion_origen:
                            raise ValidationError("Origen requerido para salida")
                        self._update_stock(StockModel, self.ubicacion_origen, self.cantidad, 'restar')

                    elif self.tipo_movimiento == self.T_TRANSFER:
                        if not self.ubicacion_origen or not self.ubicacion_destino:
                            raise ValidationError("Origen y Destino requeridos para transferencia")
                        
                        self._update_stock(StockModel, self.ubicacion_origen, self.cantidad, 'restar')
                        self._update_stock(StockModel, self.ubicacion_destino, self.cantidad, 'sumar')

                    elif self.tipo_movimiento == self.T_AJUSTE:
                        if self.ubicacion_destino:
                            self._update_stock(StockModel, self.ubicacion_destino, self.cantidad, 'sumar')
                        elif self.ubicacion_origen:
                            self._update_stock(StockModel, self.ubicacion_origen, self.cantidad, 'restar')

                    # Lógica para Orden de Compra y Ficha Técnica
                    if self.tipo_movimiento == self.T_TRANSFER:
                        # Productos que generan Orden de Compra
                        if self.content_type.model in ['pumpandmotor', 'chemicalproduct', 'pipe', 'accessory']:
                            OrdenCompra.objects.create(
                                movimiento=self,
                                solicitante=self.creado_por,
                                aprobado_por=self.aprobado_por,
                                detalles=f"Transferencia de {self.producto} de {self.ubicacion_origen} a {self.ubicacion_destino}."
                            )
                        
                        # Lógica específica para Ficha Técnica de Motores/Bombas
                        if self.content_type.model == 'pumpandmotor':
                            ficha, created = FichaTecnicaMotor.objects.get_or_create(equipo_id=self.object_id)
                            if self.ubicacion_destino.tipo == Ubicacion.TipoUbicacion.INSTALACION:
                                ficha.estado_actual = 'Instalado'
                                if not ficha.fecha_instalacion:
                                    ficha.fecha_instalacion = timezone.now().date()
                            else:
                                ficha.estado_actual = 'En Almacén'
                            ficha.save()

                if audit:
                    audit.status = InventoryAudit.STATUS_SUCCESS
                    audit.save()

        except Exception as e:
            if audit:
                audit.status = InventoryAudit.STATUS_FAILED
                audit.mensaje = str(e)
                try:
                    audit.save()
                except:
                    pass
            raise e
# Los modelos Tuberia, Equipo, StockTuberia, StockEquipo, MovimientoInventario
# se mantienen en models.py original para compatibilidad durante la transición

# ============================================================================
# SISTEMA DE ALERTAS Y NOTIFICACIONES
# ============================================================================

class Alerta(models.Model):
    """Configuración de alertas de stock bajo."""
    # Relación Genérica al Producto
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    producto = GenericForeignKey('content_type', 'object_id')
    
    acueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    umbral_minimo = models.DecimalField(max_digits=12, decimal_places=3)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Alerta de Stock'
        verbose_name_plural = 'Alertas de Stock'
        unique_together = ['content_type', 'object_id', 'acueducto']

    def __str__(self):
        return f"Alerta {self.producto} - {self.acueducto} (< {self.umbral_minimo})"


class Notificacion(models.Model):
    """Notificaciones generadas por el sistema."""
    mensaje = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, default='INFO')  # INFO, WARNING, CRITICAL
    leida = models.BooleanField(default=False)
    enviada = models.BooleanField(default=False)  # Para emails/externos
    creada_en = models.DateTimeField(auto_now_add=True)
    
    # Opcional: Relacionar con usuario si es específica
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-creada_en']

    def __str__(self):
        return f"{self.mensaje} ({self.creada_en})"


# ---------------------------------------------------------------------------
# Compatibilidad con nombres de modelos legacy (español) usados en tests
# Estos son proxies que permiten usar los nombres antiguos sin duplicar tablas
# ---------------------------------------------------------------------------


class Categoria(Category):
    class Meta:
        proxy = True
        verbose_name = 'Categoría (compat)'


class Tuberia(Pipe):
    class Meta:
        proxy = True
        verbose_name = 'Tubería (compat)'

    def __init__(self, *args, **kwargs):
        # Aceptar kwargs legacy y mapear a campos del modelo actual
        # Mapear acueducto a ubicación
        if 'acueducto' in kwargs and 'ubicacion' not in kwargs:
            acueducto = kwargs.pop('acueducto')
            ubicacion, _ = Ubicacion.objects.get_or_create(
                acueducto=acueducto,
                tipo=Ubicacion.TipoUbicacion.ALMACEN,
                defaults={'nombre': f'Almacén General {acueducto.nombre}'}
            )
            kwargs['ubicacion'] = ubicacion
        super().__init__(*args, **kwargs)


class StockEquipo(StockPumpAndMotor):
    class Meta:
        proxy = True
        verbose_name = 'StockEquipo (compat)'

    def __init__(self, *args, **kwargs):
        if 'equipo' in kwargs and 'producto' not in kwargs:
            kwargs['producto'] = kwargs.pop('equipo')
        # Mapear acueducto a ubicación
        if 'acueducto' in kwargs and 'ubicacion' not in kwargs:
            acueducto = kwargs.pop('acueducto')
            ubicacion, _ = Ubicacion.objects.get_or_create(
                acueducto=acueducto,
                tipo=Ubicacion.TipoUbicacion.ALMACEN,
                defaults={'nombre': f'Almacén General {acueducto.nombre}'}
            )
            kwargs['ubicacion'] = ubicacion
        verbose_name = 'Equipo (compat)'


class StockTuberia(StockPipe):
    class Meta:
        proxy = True
        verbose_name = 'StockTubería (compat)'

    def __init__(self, *args, **kwargs):
        # Aceptar 'tuberia' como alias para 'producto'
        if 'tuberia' in kwargs and 'producto' not in kwargs:
            kwargs['producto'] = kwargs.pop('tuberia')
        super().__init__(*args, **kwargs)


class StockEquipo(StockPumpAndMotor):
    class Meta:
        proxy = True
        verbose_name = 'StockEquipo (compat)'

    def __init__(self, *args, **kwargs):
        if 'equipo' in kwargs and 'producto' not in kwargs:
            kwargs['producto'] = kwargs.pop('equipo')
        super().__init__(*args, **kwargs)


# Alias para compatibilidad puntual
Categoria = Categoria
Tuberia = Tuberia
Equipo = Equipo
StockTuberia = StockTuberia
StockEquipo = StockEquipo



# ============================================================================
# MODELOS DE FICHA TÉCNICA Y MANTENIMIENTO
# ============================================================================

class FichaTecnicaMotor(models.Model):
    """Ficha técnica para seguimiento y mantenimiento de motores y bombas."""
    equipo = models.OneToOneField(
        'PumpAndMotor',
        on_delete=models.CASCADE,
        related_name='ficha_tecnica'
    )
    fecha_instalacion = models.DateField(null=True, blank=True)
    horas_operacion_totales = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Horas totales de operación acumuladas'
    )
    ultimo_mantenimiento = models.DateField(null=True, blank=True)
    proximo_mantenimiento = models.DateField(null=True, blank=True)
    estado_actual = models.CharField(
        max_length=50,
        default='No instalado',
        help_text='Ej: Operativo, En mantenimiento, Averiado, No instalado'
    )
    notas = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Ficha Técnica de Motor/Bomba'
        verbose_name_plural = 'Fichas Técnicas de Motores/Bombas'

    def __str__(self):
        return f"Ficha de {self.equipo.nombre}"

class RegistroMantenimiento(models.Model):
    """Registro de un mantenimiento realizado a un motor o bomba."""
    ficha_tecnica = models.ForeignKey(
        FichaTecnicaMotor,
        on_delete=models.CASCADE,
        related_name='historial_mantenimiento'
    )
    fecha = models.DateField()
    tipo_mantenimiento = models.CharField(
        max_length=50,
        choices=[
            ('PREVENTIVO', 'Preventivo'),
            ('CORRECTIVO', 'Correctivo'),
            ('PREDICTIVO', 'Predictivo')
        ]
    )
    descripcion = models.TextField()
    realizado_por = models.CharField(max_length=150)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Registro de Mantenimiento'
        verbose_name_plural = 'Registros de Mantenimiento'
        ordering = ['-fecha']

    def __str__(self):
        return f"Mantenimiento de {self.ficha_tecnica.equipo.nombre} el {self.fecha}"

# ============================================================================
# MODELO DE ORDEN DE COMPRA/TRANSFERENCIA
# ============================================================================

class OrdenCompra(models.Model):
    """Orden de compra o transferencia generada por un movimiento de inventario."""
    movimiento = models.OneToOneField(
        'MovimientoInventario',
        on_delete=models.CASCADE,
        related_name='orden_compra'
    )
    codigo_orden = models.CharField(max_length=50, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ordenes_solicitadas'
    )
    aprobador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordenes_aprobadas'
    )
    detalles = models.TextField(help_text="Detalles de la orden, producto, cantidad, origen y destino.")

    class Meta:
        verbose_name = 'Orden de Compra/Transferencia'
        verbose_name_plural = 'Órdenes de Compra/Transferencia'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.codigo_orden

    def save(self, *args, **kwargs):
        if not self.codigo_orden:
            self.codigo_orden = f"OC-{self.movimiento.id}-{timezone.now().strftime('%Y%m%d')}"
        super().save(*args, **kwargs)

