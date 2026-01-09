"""
Modelos refactorizados para Sistema de Inventario de Agua Potable y Saneamiento.
Usa Abstract Base Classes para herencia óptima de rendimiento.
"""
from django.db import models, transaction
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import uuid


# ============================================================================
# MODELOS ORGANIZACIONALES (Mantener compatibilidad)
# ============================================================================

class OrganizacionCentral(models.Model):
    """Organización central que agrupa sucursales."""
    nombre = models.CharField(max_length=200, unique=True)
    rif = models.CharField(max_length=30, blank=True, verbose_name='RIF')

    class Meta:
        verbose_name = 'Organización Central'
        verbose_name_plural = 'Organizaciones Centrales'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Sucursal(models.Model):
    """Sucursal operativa de la organización."""
    nombre = models.CharField(max_length=200, unique=True)
    organizacion_central = models.ForeignKey(
        OrganizacionCentral,
        on_delete=models.PROTECT,
        related_name='sucursales'
    )
    codigo = models.CharField(max_length=10, unique=True, blank=True)
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
    codigo = models.CharField(max_length=20, unique=True, blank=True)
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
                self.presion_psi = Decimal(str(bar * 14.5038))
            except:
                pass
        super().save(*args, **kwargs)

    def get_diametro_display(self):
        """Retorna el diámetro con su unidad."""
        return f"{self.diametro_nominal} {self.get_unidad_diametro_display()}"


# Continuará en el próximo archivo...
