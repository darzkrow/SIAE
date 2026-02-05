"""
Tareas Models - Task Scheduling Module

Sistema de programación de tareas con soporte para:
- Asignaciones múltiples
- Tareas recurrentes
- Vinculación a entidades del sistema
- Subtareas y comentarios
- Visualización Kanban
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from core.models import TimeStampedModel
import logging

import logging
from .choices import (
    TipoColumnaKanban, PrioridadTarea, EstadoTarea, PatronRecurrencia,
    RolAsignacion, TipoRecordatorio, AccionHistorial
)

User = get_user_model()
logger = logging.getLogger(__name__)


# =============================================================================
# CATEGORÍAS DE TAREAS
# =============================================================================

class CategoriaTarea(TimeStampedModel):
    """
    Categorías para organizar tareas.
    
    Ejemplos: Mantenimiento, Administrativa, Operativa, Urgente
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        help_text='Nombre de la categoría'
    )
    codigo = models.CharField(
        max_length=20,
        unique=True,
        help_text='Código corto (ej: MANT, ADMIN)'
    )
    color = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text='Color en formato hexadecimal'
    )
    icono = models.CharField(
        max_length=50,
        blank=True,
        default='task',
        help_text='Nombre del icono (para UI)'
    )
    descripcion = models.TextField(
        blank=True,
        help_text='Descripción de la categoría'
    )
    orden = models.PositiveIntegerField(
        default=0,
        help_text='Orden de visualización'
    )
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Categoría de Tarea'
        verbose_name_plural = 'Categorías de Tareas'
        ordering = ['orden', 'nombre']
        indexes = [
            models.Index(fields=['activo']),
            models.Index(fields=['codigo']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


# =============================================================================
# COLUMNAS KANBAN
# =============================================================================

class ColumnaKanban(TimeStampedModel):
    """
    Columnas personalizables para el tablero Kanban.
    
    Por defecto: Pendiente, En Progreso, Completada
    """
    nombre = models.CharField(
        max_length=50,
        help_text='Nombre de la columna'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoColumnaKanban.choices,
        default='PROGRESO',
        help_text='Tipo de columna'
    )
    color = models.CharField(
        max_length=7,
        default='#6B7280',
        help_text='Color de la columna'
    )
    orden = models.PositiveIntegerField(
        default=0,
        help_text='Posición en el tablero'
    )
    limite_tareas = models.PositiveIntegerField(
        default=0,
        help_text='Límite máximo de tareas (0 = sin límite)'
    )
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Columna Kanban'
        verbose_name_plural = 'Columnas Kanban'
        ordering = ['orden']
    
    def __str__(self):
        return self.nombre


# =============================================================================
# MODELO PRINCIPAL DE TAREA
# =============================================================================

class Tarea(TimeStampedModel):
    """
    Tarea programable con soporte completo para gestión.
    
    Características:
    - Prioridades y estados
    - Fechas de inicio y vencimiento
    - Subtareas (tareas hijas)
    - Recurrencia automática
    - Vinculación a entidades del sistema
    """
    
    # Prioridad y estado
    prioridad = models.CharField(
        max_length=10,
        choices=PrioridadTarea.choices,
        default='MEDIA'
    )
    estado = models.CharField(
        max_length=15,
        choices=EstadoTarea.choices,
        default='PENDIENTE'
    )
    
    # Fechas
    fecha_inicio = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha de inicio planificada'
    )
    fecha_vencimiento = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha límite'
    )
    fecha_completada = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha en que se completó'
    )
    
    # Progreso
    porcentaje_completado = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Porcentaje de avance (0-100)'
    )
    
    # Subtareas
    tarea_padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtareas',
        help_text='Tarea principal (si es subtarea)'
    )
    orden_subtarea = models.PositiveIntegerField(
        default=0,
        help_text='Orden dentro de la tarea padre'
    )
    
    # Recurrencia
    es_recurrente = models.BooleanField(
        default=False,
        help_text='Si la tarea se repite automáticamente'
    )
    patron_recurrencia = models.CharField(
        max_length=15,
        choices=PatronRecurrencia.choices,
        blank=True,
        help_text='Patrón de repetición'
    )
    intervalo_recurrencia = models.PositiveIntegerField(
        default=1,
        help_text='Cada cuántos períodos se repite'
    )
    recurrencia_activa = models.BooleanField(
        default=True,
        help_text='Si la recurrencia está activa'
    )
    tarea_origen = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tareas_generadas',
        help_text='Tarea original que generó esta recurrencia'
    )
    
    # Vinculación a entidades del sistema (GenericForeignKey)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Tipo de entidad vinculada'
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='ID de la entidad vinculada'
    )
    entidad_vinculada = GenericForeignKey('content_type', 'object_id')
    
    # Creación
    creador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='tareas_creadas',
        help_text='Usuario que creó la tarea'
    )
    
    # Etiquetas
    etiquetas = models.CharField(
        max_length=500,
        blank=True,
        help_text='Etiquetas separadas por coma'
    )
    
    class Meta:
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'
        ordering = ['-prioridad', 'fecha_vencimiento', '-created_at']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['prioridad']),
            models.Index(fields=['fecha_vencimiento']),
            models.Index(fields=['creador']),
            models.Index(fields=['es_recurrente']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['tarea_padre']),
            models.Index(fields=['columna_kanban', 'orden_subtarea']),
        ]
    
    def __str__(self):
        return f"{self.titulo} [{self.get_estado_display()}]"
    
    @property
    def esta_vencida(self):
        """Verifica si la tarea está vencida"""
        if not self.fecha_vencimiento:
            return False
        if self.estado in ['COMPLETADA', 'CANCELADA']:
            return False
        return timezone.now() > self.fecha_vencimiento
    
    @property
    def dias_para_vencer(self):
        """Días restantes para el vencimiento"""
        if not self.fecha_vencimiento:
            return None
        delta = self.fecha_vencimiento - timezone.now()
        return delta.days
    
    def completar(self, usuario=None):
        """Marca la tarea como completada"""
        self.estado = 'COMPLETADA'
        self.porcentaje_completado = 100
        self.fecha_completada = timezone.now()
        self.save()
        
        # Si es recurrente, generar la siguiente
        if self.es_recurrente and self.recurrencia_activa:
            self.generar_siguiente_recurrencia()
        
        # Registrar en historial
        HistorialTarea.objects.create(
            tarea=self,
            usuario=usuario,
            accion='COMPLETADA',
            descripcion='Tarea marcada como completada'
        )
    
    def generar_siguiente_recurrencia(self):
        """Genera la siguiente tarea recurrente"""
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta
        
        # Calcular nueva fecha de vencimiento
        if not self.fecha_vencimiento:
            nueva_fecha = timezone.now()
        else:
            nueva_fecha = self.fecha_vencimiento
        
        intervalo = self.intervalo_recurrencia
        
        if self.patron_recurrencia == 'DIARIO':
            nueva_fecha += timedelta(days=intervalo)
        elif self.patron_recurrencia == 'SEMANAL':
            nueva_fecha += timedelta(weeks=intervalo)
        elif self.patron_recurrencia == 'QUINCENAL':
            nueva_fecha += timedelta(weeks=2 * intervalo)
        elif self.patron_recurrencia == 'MENSUAL':
            nueva_fecha += relativedelta(months=intervalo)
        elif self.patron_recurrencia == 'TRIMESTRAL':
            nueva_fecha += relativedelta(months=3 * intervalo)
        elif self.patron_recurrencia == 'ANUAL':
            nueva_fecha += relativedelta(years=intervalo)
        
        # Crear nueva tarea
        nueva_tarea = Tarea.objects.create(
            titulo=self.titulo,
            descripcion=self.descripcion,
            categoria=self.categoria,
            prioridad=self.prioridad,
            estado='PENDIENTE',
            fecha_vencimiento=nueva_fecha,
            es_recurrente=True,
            patron_recurrencia=self.patron_recurrencia,
            intervalo_recurrencia=self.intervalo_recurrencia,
            recurrencia_activa=True,
            tarea_origen=self.tarea_origen or self,
            creador=self.creador,
            content_type=self.content_type,
            object_id=self.object_id,
            etiquetas=self.etiquetas,
        )
        
        # Copiar asignaciones
        for asignacion in self.asignaciones.all():
            AsignacionTarea.objects.create(
                tarea=nueva_tarea,
                usuario=asignacion.usuario,
                rol=asignacion.rol,
                asignado_por=asignacion.asignado_por,
            )
        
        logger.info(f"Generada nueva tarea recurrente: {nueva_tarea.titulo}")
        return nueva_tarea


# =============================================================================
# ASIGNACIONES DE TAREAS
# =============================================================================

class AsignacionTarea(TimeStampedModel):
    """
    Asignación de tareas a usuarios.
    
    Roles: Responsable (principal), Colaborador, Observador
    """
    
    tarea = models.ForeignKey(
        Tarea,
        on_delete=models.CASCADE,
        related_name='asignaciones',
        help_text='Tarea asignada'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tareas_asignadas',
        help_text='Usuario asignado'
    )
    rol = models.CharField(
        max_length=15,
        choices=RolAsignacion.choices,
        default='RESPONSABLE',
        help_text='Rol en la tarea'
    )
    asignado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='asignaciones_realizadas',
        help_text='Quién realizó la asignación'
    )
    notificado = models.BooleanField(
        default=False,
        help_text='Si el usuario fue notificado'
    )
    
    class Meta:
        verbose_name = 'Asignación de Tarea'
        verbose_name_plural = 'Asignaciones de Tareas'
        unique_together = ['tarea', 'usuario']
        indexes = [
            models.Index(fields=['usuario', 'rol']),
            models.Index(fields=['tarea']),
        ]
    
    def __str__(self):
        return f"{self.usuario.username} - {self.tarea.titulo} ({self.get_rol_display()})"


# =============================================================================
# COMENTARIOS EN TAREAS
# =============================================================================

class ComentarioTarea(TimeStampedModel):
    """
    Comentarios para colaboración en tareas.
    """
    tarea = models.ForeignKey(
        Tarea,
        on_delete=models.CASCADE,
        related_name='comentarios',
        help_text='Tarea comentada'
    )
    autor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comentarios_tareas',
        help_text='Autor del comentario'
    )
    contenido = models.TextField(
        help_text='Contenido del comentario'
    )
    
    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.autor.username}: {self.contenido[:50]}..."


# =============================================================================
# ARCHIVOS ADJUNTOS
# =============================================================================

class ArchivoAdjunto(TimeStampedModel):
    """
    Archivos adjuntos a tareas.
    """
    tarea = models.ForeignKey(
        Tarea,
        on_delete=models.CASCADE,
        related_name='archivos',
        help_text='Tarea'
    )
    archivo = models.FileField(
        upload_to='tareas/adjuntos/%Y/%m/',
        help_text='Archivo'
    )
    nombre = models.CharField(
        max_length=255,
        help_text='Nombre del archivo'
    )
    descripcion = models.TextField(
        blank=True,
        help_text='Descripción del archivo'
    )
    subido_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='archivos_subidos',
        help_text='Usuario que subió el archivo'
    )
    
    class Meta:
        verbose_name = 'Archivo Adjunto'
        verbose_name_plural = 'Archivos Adjuntos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.nombre} - {self.tarea.titulo}"


# =============================================================================
# RECORDATORIOS
# =============================================================================

class RecordatorioTarea(TimeStampedModel):
    """
    Recordatorios programados para tareas.
    """
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recordatorios',
        help_text='Usuario a notificar'
    )
    fecha_recordatorio = models.DateTimeField(
        help_text='Fecha y hora del recordatorio'
    )
    tipo = models.CharField(
        max_length=10,
        choices=TipoRecordatorio.choices,
        default='PUSH',
        help_text='Tipo de notificación'
    )
    mensaje = models.CharField(
        max_length=255,
        blank=True,
        help_text='Mensaje personalizado'
    )
    enviado = models.BooleanField(
        default=False,
        help_text='Si ya se envió el recordatorio'
    )
    fecha_envio = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha en que se envió'
    )
    
    class Meta:
        verbose_name = 'Recordatorio'
        verbose_name_plural = 'Recordatorios'
        ordering = ['fecha_recordatorio']
        indexes = [
            models.Index(fields=['fecha_recordatorio', 'enviado']),
            models.Index(fields=['usuario']),
        ]
    
    def __str__(self):
        return f"Recordatorio: {self.tarea.titulo} - {self.usuario.username}"


# =============================================================================
# HISTORIAL DE TAREAS
# =============================================================================

class HistorialTarea(TimeStampedModel):
    """
    Registro de cambios y acciones en tareas.
    """
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='historial_tareas',
        help_text='Usuario que realizó la acción'
    )
    accion = models.CharField(
        max_length=25,
        choices=AccionHistorial.choices,
        help_text='Tipo de acción'
    )
    descripcion = models.TextField(
        blank=True,
        help_text='Descripción detallada del cambio'
    )
    datos_anteriores = models.JSONField(
        null=True,
        blank=True,
        help_text='Datos antes del cambio'
    )
    datos_nuevos = models.JSONField(
        null=True,
        blank=True,
        help_text='Datos después del cambio'
    )
    
    class Meta:
        verbose_name = 'Historial de Tarea'
        verbose_name_plural = 'Historial de Tareas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tarea.titulo} - {self.get_accion_display()}"
