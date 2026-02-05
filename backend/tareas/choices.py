"""
Opciones para modelos de la aplicación tareas.
"""
from django.db import models

class TipoColumnaKanban(models.TextChoices):
        INICIO = 'INICIO', 'Estado Inicial'
        PROGRESO = 'PROGRESO', 'En Progreso'
        REVISION = 'REVISION', 'En Revisión/Bloqueado'
        FIN = 'FIN', 'Estado Final'

class PrioridadTarea(models.TextChoices):
        BAJA = 'BAJA', 'Baja'
        MEDIA = 'MEDIA', 'Media'
        ALTA = 'ALTA', 'Alta'
        URGENTE = 'URGENTE', 'Urgente'

class EstadoTarea(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_PROGRESO = 'EN_PROGRESO', 'En Progreso'
        EN_REVISION = 'EN_REVISION', 'En Revisión'
        BLOQUEADA = 'BLOQUEADA', 'Bloqueada'
        COMPLETADA = 'COMPLETADA', 'Completada'
        CANCELADA = 'CANCELADA', 'Cancelada'

class PatronRecurrencia(models.TextChoices):
        DIARIO = 'DIARIO', 'Diario'
        SEMANAL = 'SEMANAL', 'Semanal'
        QUINCENAL = 'QUINCENAL', 'Quincenal'
        MENSUAL = 'MENSUAL', 'Mensual'
        TRIMESTRAL = 'TRIMESTRAL', 'Trimestral'
        ANUAL = 'ANUAL', 'Anual'

class RolAsignacion(models.TextChoices):
        RESPONSABLE = 'RESPONSABLE', 'Responsable'
        COLABORADOR = 'COLABORADOR', 'Colaborador'
        OBSERVADOR = 'OBSERVADOR', 'Observador'

class TipoRecordatorio(models.TextChoices):
        PUSH = 'PUSH', 'Notificación Push'
        EMAIL = 'EMAIL', 'Correo Electrónico'
        TELEGRAM = 'TELEGRAM', 'Telegram'

class AccionHistorial(models.TextChoices):
        CREADA = 'CREADA', 'Tarea Creada'
        EDITADA = 'EDITADA', 'Tarea Editada'
        ASIGNADA = 'ASIGNADA', 'Tarea Asignada'
        DESASIGNADA = 'DESASIGNADA', 'Asignación Removida'
        ESTADO_CAMBIADO = 'ESTADO_CAMBIADO', 'Estado Cambiado'
        PRIORIDAD_CAMBIADA = 'PRIORIDAD_CAMBIADA', 'Prioridad Cambiada'
        FECHA_CAMBIADA = 'FECHA_CAMBIADA', 'Fecha Modificada'
        COMENTARIO = 'COMENTARIO', 'Comentario Agregado'
        ARCHIVO = 'ARCHIVO', 'Archivo Adjuntado'
        COMPLETADA = 'COMPLETADA', 'Tarea Completada'
        CANCELADA = 'CANCELADA', 'Tarea Cancelada'
        REABIERTA = 'REABIERTA', 'Tarea Reabierta'
        RECURRENCIA_GENERADA = 'RECURRENCIA_GENERADA', 'Recurrencia Generada'
