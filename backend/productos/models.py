from django.db import models, transaction
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from catalogo.models import CategoriaProducto, Marca, Tag
from core.models import SoftDeleteModel, TimeStampedModel
from proveedores.models import Supplier

class UnitOfMeasure(SoftDeleteModel):
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
        db_table = 'inventario_unitofmeasure'
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'
        ordering = ['tipo', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.simbolo})"

    def __str__(self):
        return f"{self.nombre} ({self.simbolo})"

class ProductBase(SoftDeleteModel):
    sku = models.CharField(max_length=50, unique=True, verbose_name='SKU')
    nombre = models.CharField(max_length=250)
    descripcion = models.TextField(blank=True)
    
    class TipoInventario(models.TextChoices):
        ESTRATEGICO = 'ESTRATEGICO', 'Estratégico Hídrico'
        OPERACIONAL = 'OPERACIONAL', 'Operacional'
        CONSUMIBLE = 'CONSUMIBLE', 'Consumible'
        ACTIVO_FIJO = 'ACTIVO_FIJO', 'Activo Fijo'
    
    tipo_inventario = models.CharField(max_length=20, choices=TipoInventario.choices, default=TipoInventario.OPERACIONAL)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.PROTECT, related_name='%(class)s_productos')
    unidad_medida = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT, related_name='%(class)s_productos')
    
    tags = models.ManyToManyField(Tag, blank=True, related_name='%(class)s_products')
    custom_fields = models.JSONField(default=dict, blank=True)
    search_vector = SearchVectorField(null=True, blank=True)
    
    es_critico = models.BooleanField(default=False)
    nivel_criticidad = models.CharField(
        max_length=10,
        choices=[('BAJO', 'Bajo'), ('MEDIO', 'Medio'), ('ALTO', 'Alto'), ('CRITICO', 'Crítico')],
        default='MEDIO'
    )
    
    stock_actual = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal('0.000'))
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal('0.000'))
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    proveedor = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='%(class)s_productos')
    activo = models.BooleanField(default=True)
    fecha_entrada = models.DateField(default=timezone.now)
    notas = models.TextField(blank=True)

    class Meta:
        abstract = True
        ordering = ['sku']
        indexes = [GinIndex(fields=['search_vector'])]

    def __str__(self):
        return f"{self.sku} - {self.nombre}"

    def generate_sku(self):
        categoria_code = self.categoria.codigo if self.categoria else 'GEN'
        tipo_code = self.__class__.__name__[:3].upper()
        last_product = self.__class__.objects.filter(sku__startswith=f"{categoria_code}-{tipo_code}-").order_by('-sku').first()
        new_number = (int(last_product.sku.split('-')[-1]) + 1) if last_product else 1
        return f"{categoria_code}-{tipo_code}-{new_number:04d}"

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = self.generate_sku()
        super().save(*args, **kwargs)

class ChemicalProduct(ProductBase):
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

    es_peligroso = models.BooleanField(default=False)
    nivel_peligrosidad = models.CharField(max_length=15, choices=NivelPeligrosidad.choices, blank=True)
    fecha_caducidad = models.DateField(null=True, blank=True)
    concentracion = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    presentacion = models.CharField(max_length=20, choices=TipoPresentacion.choices, default=TipoPresentacion.SACO)
    
    class Meta:
        db_table = 'inventario_chemicalproduct'
        verbose_name = 'Producto Químico'
        verbose_name_plural = 'Productos Químicos'

class Pipe(ProductBase):
    class Material(models.TextChoices):
        PVC = 'PVC', 'PVC'
        PEAD = 'PEAD', 'PEAD'
        ACERO = 'ACERO', 'Acero'
        HIERRO = 'HIERRO_DUCTIL', 'Hierro Dúctil'

    material = models.CharField(max_length=20, choices=Material.choices)
    diametro_nominal = models.DecimalField(max_digits=8, decimal_places=2)
    presion_nominal = models.CharField(max_length=10)
    presion_psi = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    tipo_uso = models.CharField(max_length=20, blank=True)
    
    class Meta:
        db_table = 'inventario_pipe'
        verbose_name = 'Tubería'
        verbose_name_plural = 'Tuberías'

class PumpAndMotor(ProductBase):
    class TipoEquipo(models.TextChoices):
        BOMBA = 'BOMBA', 'Bomba'
        MOTOR = 'MOTOR', 'Motor'
    
    tipo_equipo = models.CharField(max_length=30, choices=TipoEquipo.choices, default='BOMBA')
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name='equipos')
    modelo = models.CharField(max_length=150)
    potencia_hp = models.DecimalField(max_digits=8, decimal_places=2)
    potencia_kw = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    voltaje = models.IntegerField()
    
    class Meta:
        db_table = 'inventario_pumpandmotor'
        verbose_name = 'Bomba y Motor'
        verbose_name_plural = 'Bombas y Motores'

class Accessory(ProductBase):
    tipo_accesorio = models.CharField(max_length=20)
    tipo_conexion = models.CharField(max_length=20, blank=True)
    diametro_entrada = models.DecimalField(max_digits=8, decimal_places=2)
    material = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'inventario_accessory'
        verbose_name = 'Accesorio'
        verbose_name_plural = 'Accesorios'
