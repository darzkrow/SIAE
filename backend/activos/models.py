from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from core.models import TimeStampedModel
from geography.models import Ubicacion
from productos.models import PumpAndMotor
from proveedores.models import Supplier

class MaterialEstrategico(TimeStampedModel):
    """🛡️ Información adicional para materiales estratégicos hídricos"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    producto = GenericForeignKey('content_type', 'object_id')
    
    nivel_criticidad = models.CharField(
        max_length=10,
        choices=[('BAJO', 'Bajo'), ('MEDIO', 'Medio'), ('ALTO', 'Alto'), ('CRITICO', 'Crítico')],
        default='MEDIO'
    )
    plan_contingencia = models.TextField(blank=True)
    proveedor_alternativo = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='materiales_estrategicos_alternativos'
    )
    stock_seguridad_dias = models.IntegerField(default=90)
    requiere_aprobacion_especial = models.BooleanField(default=True)
    prioridad_reposicion = models.CharField(
        max_length=10,
        choices=[('BAJA', 'Baja'), ('MEDIA', 'Media'), ('ALTA', 'Alta')],
        default='MEDIA'
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='materiales_estrategicos_asignados'
    )

    class Meta:
        db_table = 'inventario_materialestrategico'
        verbose_name = 'Material Estratégico'
        verbose_name_plural = 'Materiales Estratégicos'

class ActivoFijo(TimeStampedModel):
    """🏗️ Gestión de Activos Fijos"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    producto = GenericForeignKey('content_type', 'object_id')
    
    valor_adquisicion = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_adquisicion = models.DateField()
    vida_util_anos = models.IntegerField()
    valor_residual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    estado_fisico = models.CharField(
        max_length=20,
        choices=[('EXCELENTE', 'Excelente'), ('BUENO', 'Bueno'), ('REGULAR', 'Regular'), ('MALO', 'Malo'), ('FUERA_SERVICIO', 'Fuera de Servicio')],
        default='BUENO'
    )
    estado_depreciacion = models.CharField(
        max_length=20,
        choices=[('NUEVO', 'Nuevo'), ('EN_USO', 'En Uso'), ('DEPRECIADO', 'Depreciado')],
        default='EN_USO'
    )
    
    codigo_activo = models.CharField(max_length=50, unique=True)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.PROTECT, related_name='activos_fijos_new')
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='activos_fijos_asignados_new'
    )

    class Meta:
        db_table = 'inventario_activofijo'
        verbose_name = 'Activo Fijo'
        verbose_name_plural = 'Activos Fijos'

class FichaTecnicaMotor(models.Model):
    """Ficha técnica para motores y bombas."""
    equipo = models.OneToOneField(PumpAndMotor, on_delete=models.CASCADE, related_name='ficha_tecnica_new')
    fecha_instalacion = models.DateField(null=True, blank=True)
    horas_operacion_totales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado_actual = models.CharField(max_length=50, default='No instalado')
    
    # Specs
    potencia_nominal_kw = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tension_v = models.IntegerField(null=True, blank=True)
    frecuencia_hz = models.IntegerField(default=60)
    clase_aislamiento = models.CharField(max_length=10, blank=True)
    numero_fases = models.IntegerField(default=3)

    class Meta:
        db_table = 'inventario_fichatecnicamotor'
        verbose_name = 'Ficha Técnica'

class RegistroMantenimiento(models.Model):
    """Registro de mantenimiento."""
    ficha_tecnica = models.ForeignKey(FichaTecnicaMotor, on_delete=models.CASCADE, related_name='historial')
    fecha = models.DateField(default=timezone.now)
    tipo_mantenimiento = models.CharField(
        max_length=50,
        choices=[('PREVENTIVO', 'Preventivo'), ('CORRECTIVO', 'Correctivo'), ('PREDICTIVO', 'Predictivo')]
    )
    prioridad = models.CharField(
        max_length=10,
        choices=[('BAJA', 'Baja'), ('MEDIA', 'Media'), ('ALTA', 'Alta')],
        default='MEDIA'
    )
    descripcion = models.TextField()
    realizado_por = models.CharField(max_length=150)
    realizado = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inventario_registromantenimiento'
        verbose_name = 'Registro de Mantenimiento'
        verbose_name_plural = 'Registros de Mantenimiento'
