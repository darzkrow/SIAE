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
            self.potencia_kw = self.potencia_hp * Decimal('0.7457')
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
    """Stock de productos químicos por acueducto."""
    producto = models.ForeignKey(
        ChemicalProduct,
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    acueducto = models.ForeignKey(
        Acueducto,
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
    ubicacion_fisica = models.CharField(
        max_length=100,
        blank=True,
        help_text='Ubicación física en almacén'
    )
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Stock de Químico'
        verbose_name_plural = 'Stocks de Químicos'
        unique_together = ('producto', 'acueducto', 'lote')
        ordering = ['producto', 'acueducto']
        indexes = [
            models.Index(fields=['producto', 'acueducto']),
            models.Index(fields=['fecha_vencimiento']),
        ]

    def __str__(self):
        return f"{self.producto.nombre} @ {self.acueducto}: {self.cantidad}"


class StockPipe(models.Model):
    """Stock de tuberías por acueducto."""
    producto = models.ForeignKey(
        Pipe,
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    acueducto = models.ForeignKey(
        Acueducto,
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
    ubicacion_fisica = models.CharField(max_length=100, blank=True)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Stock de Tubería'
        verbose_name_plural = 'Stocks de Tuberías'
        unique_together = ('producto', 'acueducto')
        ordering = ['producto', 'acueducto']
        indexes = [
            models.Index(fields=['producto', 'acueducto']),
        ]

    def save(self, *args, **kwargs):
        # Calcular metros totales automáticamente
        if self.producto and self.cantidad:
            self.metros_totales = self.cantidad * self.producto.longitud_unitaria
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.nombre} @ {self.acueducto}: {self.cantidad} un ({self.metros_totales}m)"
