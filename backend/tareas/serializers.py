"""
Tareas Serializers - Task Scheduling Module
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from .models import (
    CategoriaTarea,
    ColumnaKanban,
    Tarea,
    AsignacionTarea,
    ComentarioTarea,
    ArchivoAdjunto,
    RecordatorioTarea,
    HistorialTarea,
)
from .choices import EstadoTarea, RolAsignacion

User = get_user_model()


# =============================================================================
# SERIALIZERS AUXILIARES
# =============================================================================

class UsuarioSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple para usuarios"""
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'nombre_completo']
    
    def get_nombre_completo(self, obj):
        return obj.get_full_name() or obj.username


class CategoriaTareaSerializer(serializers.ModelSerializer):
    """Serializer para categorías de tareas"""
    tareas_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CategoriaTarea
        fields = [
            'id', 'nombre', 'codigo', 'color', 'icono',
            'descripcion', 'orden', 'activo', 'tareas_count'
        ]
        read_only_fields = ['tareas_count']
    
    def get_tareas_count(self, obj):
        return obj.tareas.filter(estado__in=['PENDIENTE', 'EN_PROGRESO']).count()


class ColumnaKanbanSerializer(serializers.ModelSerializer):
    """Serializer para columnas del tablero Kanban"""
    tareas_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ColumnaKanban
        fields = [
            'id', 'nombre', 'tipo', 'color', 'orden',
            'limite_tareas', 'activo', 'tareas_count'
        ]
    
    def get_tareas_count(self, obj):
        return obj.tareas.count()


# =============================================================================
# SERIALIZERS DE COMENTARIOS Y ARCHIVOS
# =============================================================================

class ComentarioTareaSerializer(serializers.ModelSerializer):
    """Serializer para comentarios"""
    autor = UsuarioSimpleSerializer(read_only=True)
    
    class Meta:
        model = ComentarioTarea
        fields = ['id', 'tarea', 'autor', 'contenido', 'created_at']
        read_only_fields = ['autor', 'created_at']
    
    def create(self, validated_data):
        validated_data['autor'] = self.context['request'].user
        comentario = super().create(validated_data)
        
        # Registrar en historial
        HistorialTarea.objects.create(
            tarea=comentario.tarea,
            usuario=comentario.autor,
            accion='COMENTARIO',
            descripcion=f'Comentario agregado: {comentario.contenido[:100]}...'
        )
        return comentario


class ArchivoAdjuntoSerializer(serializers.ModelSerializer):
    """Serializer para archivos adjuntos"""
    subido_por = UsuarioSimpleSerializer(read_only=True)
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = ArchivoAdjunto
        fields = [
            'id', 'tarea', 'archivo', 'nombre', 'descripcion',
            'subido_por', 'created_at', 'url'
        ]
        read_only_fields = ['subido_por', 'created_at']
    
    def get_url(self, obj):
        if obj.archivo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.archivo.url)
            return obj.archivo.url
        return None
    
    def create(self, validated_data):
        validated_data['subido_por'] = self.context['request'].user
        if not validated_data.get('nombre') and validated_data.get('archivo'):
            validated_data['nombre'] = validated_data['archivo'].name
        return super().create(validated_data)


class RecordatorioTareaSerializer(serializers.ModelSerializer):
    """Serializer para recordatorios"""
    usuario = UsuarioSimpleSerializer(read_only=True)
    
    class Meta:
        model = RecordatorioTarea
        fields = [
            'id', 'tarea', 'usuario', 'fecha_recordatorio',
            'tipo', 'mensaje', 'enviado', 'fecha_envio', 'created_at'
        ]
        read_only_fields = ['enviado', 'fecha_envio']


class HistorialTareaSerializer(serializers.ModelSerializer):
    """Serializer para historial"""
    usuario = UsuarioSimpleSerializer(read_only=True)
    accion_display = serializers.CharField(source='get_accion_display', read_only=True)
    
    class Meta:
        model = HistorialTarea
        fields = [
            'id', 'tarea', 'usuario', 'accion', 'accion_display',
            'descripcion', 'datos_anteriores', 'datos_nuevos', 'created_at'
        ]


# =============================================================================
# SERIALIZERS DE ASIGNACIONES
# =============================================================================

class AsignacionTareaSerializer(serializers.ModelSerializer):
    """Serializer para asignaciones"""
    usuario = UsuarioSimpleSerializer(read_only=True)
    usuario_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='usuario',
        write_only=True
    )
    asignado_por = UsuarioSimpleSerializer(read_only=True)
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    
    class Meta:
        model = AsignacionTarea
        fields = [
            'id', 'tarea', 'usuario', 'usuario_id', 'rol', 'rol_display',
            'asignado_por', 'notificado', 'created_at'
        ]
        read_only_fields = ['asignado_por', 'notificado']
    
    def create(self, validated_data):
        validated_data['asignado_por'] = self.context['request'].user
        asignacion = super().create(validated_data)
        
        # Registrar en historial
        HistorialTarea.objects.create(
            tarea=asignacion.tarea,
            usuario=validated_data['asignado_por'],
            accion='ASIGNADA',
            descripcion=f'Asignado a {asignacion.usuario.username} como {asignacion.get_rol_display()}'
        )
        return asignacion


# =============================================================================
# SERIALIZERS DE TAREAS
# =============================================================================

class TareaListSerializer(serializers.ModelSerializer):
    """Serializer resumido para listados"""
    categoria = CategoriaTareaSerializer(read_only=True)
    columna_kanban = ColumnaKanbanSerializer(read_only=True)
    creador = UsuarioSimpleSerializer(read_only=True)
    asignados = serializers.SerializerMethodField()
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    esta_vencida = serializers.BooleanField(read_only=True)
    dias_para_vencer = serializers.IntegerField(read_only=True)
    subtareas_count = serializers.SerializerMethodField()
    comentarios_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tarea
        fields = [
            'id', 'titulo', 'descripcion', 'categoria', 'columna_kanban',
            'prioridad', 'prioridad_display', 'estado', 'estado_display',
            'fecha_inicio', 'fecha_vencimiento', 'fecha_completada',
            'porcentaje_completado', 'creador', 'asignados',
            'esta_vencida', 'dias_para_vencer', 'es_recurrente',
            'subtareas_count', 'comentarios_count', 'etiquetas',
            'created_at'
        ]
    
    def get_asignados(self, obj):
        asignaciones = obj.asignaciones.select_related('usuario').all()
        return [{
            'id': a.usuario.id,
            'username': a.usuario.username,
            'nombre': a.usuario.get_full_name() or a.usuario.username,
            'rol': a.rol
        } for a in asignaciones]
    
    def get_subtareas_count(self, obj):
        return obj.subtareas.count()
    
    def get_comentarios_count(self, obj):
        return obj.comentarios.count()


class SubtareaSerializer(serializers.ModelSerializer):
    """Serializer para subtareas"""
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Tarea
        fields = [
            'id', 'titulo', 'estado', 'estado_display',
            'porcentaje_completado', 'orden_subtarea', 'fecha_vencimiento'
        ]


class TareaDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para una tarea"""
    categoria = CategoriaTareaSerializer(read_only=True)
    columna_kanban = ColumnaKanbanSerializer(read_only=True)
    creador = UsuarioSimpleSerializer(read_only=True)
    asignaciones = AsignacionTareaSerializer(many=True, read_only=True)
    comentarios = ComentarioTareaSerializer(many=True, read_only=True)
    archivos = ArchivoAdjuntoSerializer(many=True, read_only=True)
    recordatorios = RecordatorioTareaSerializer(many=True, read_only=True)
    subtareas = SubtareaSerializer(many=True, read_only=True)
    tarea_padre_info = serializers.SerializerMethodField()
    entidad_info = serializers.SerializerMethodField()
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    patron_recurrencia_display = serializers.CharField(
        source='get_patron_recurrencia_display', read_only=True
    )
    esta_vencida = serializers.BooleanField(read_only=True)
    dias_para_vencer = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Tarea
        fields = [
            'id', 'titulo', 'descripcion', 'categoria', 'columna_kanban',
            'prioridad', 'prioridad_display', 'estado', 'estado_display',
            'fecha_inicio', 'fecha_vencimiento', 'fecha_completada',
            'porcentaje_completado', 'creador',
            'tarea_padre', 'tarea_padre_info', 'orden_subtarea',
            'es_recurrente', 'patron_recurrencia', 'patron_recurrencia_display',
            'intervalo_recurrencia', 'recurrencia_activa',
            'content_type', 'object_id', 'entidad_info',
            'etiquetas', 'esta_vencida', 'dias_para_vencer',
            'asignaciones', 'comentarios', 'archivos', 'recordatorios', 'subtareas',
            'created_at', 'updated_at'
        ]
    
    def get_tarea_padre_info(self, obj):
        if obj.tarea_padre:
            return {
                'id': obj.tarea_padre.id,
                'titulo': obj.tarea_padre.titulo
            }
        return None
    
    def get_entidad_info(self, obj):
        if obj.content_type and obj.object_id:
            try:
                entidad = obj.entidad_vinculada
                return {
                    'tipo': obj.content_type.model,
                    'app': obj.content_type.app_label,
                    'id': obj.object_id,
                    'nombre': str(entidad) if entidad else 'No encontrada'
                }
            except Exception:
                return None
        return None


class TareaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear tareas"""
    asignados = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    entidad_tipo = serializers.CharField(write_only=True, required=False)
    entidad_app = serializers.CharField(write_only=True, required=False)
    entidad_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Tarea
        fields = [
            'titulo', 'descripcion', 'categoria', 'columna_kanban',
            'prioridad', 'estado', 'fecha_inicio', 'fecha_vencimiento',
            'tarea_padre', 'orden_subtarea',
            'es_recurrente', 'patron_recurrencia', 'intervalo_recurrencia',
            'etiquetas', 'asignados',
            'entidad_tipo', 'entidad_app', 'entidad_id'
        ]
    
    def create(self, validated_data):
        asignados = validated_data.pop('asignados', [])
        entidad_tipo = validated_data.pop('entidad_tipo', None)
        entidad_app = validated_data.pop('entidad_app', None)
        entidad_id = validated_data.pop('entidad_id', None)
        
        # Vincular entidad si se especifica
        if entidad_tipo and entidad_app and entidad_id:
            try:
                content_type = ContentType.objects.get(
                    app_label=entidad_app,
                    model=entidad_tipo.lower()
                )
                validated_data['content_type'] = content_type
                validated_data['object_id'] = entidad_id
            except ContentType.DoesNotExist:
                pass
        
        validated_data['creador'] = self.context['request'].user
        tarea = super().create(validated_data)
        
        # Crear asignaciones
        for usuario_id in asignados:
            try:
                usuario = User.objects.get(pk=usuario_id)
                AsignacionTarea.objects.create(
                    tarea=tarea,
                    usuario=usuario,
                    rol='RESPONSABLE' if usuario_id == asignados[0] else 'COLABORADOR',
                    asignado_por=tarea.creador
                )
            except User.DoesNotExist:
                pass
        
        # Registrar en historial
        HistorialTarea.objects.create(
            tarea=tarea,
            usuario=tarea.creador,
            accion='CREADA',
            descripcion=f'Tarea creada: {tarea.titulo}'
        )
        
        return tarea


class TareaKanbanSerializer(serializers.ModelSerializer):
    """Serializer para vista Kanban"""
    asignados = serializers.SerializerMethodField()
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    categoria_color = serializers.CharField(source='categoria.color', read_only=True)
    comentarios_count = serializers.SerializerMethodField()
    esta_vencida = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Tarea
        fields = [
            'id', 'titulo', 'prioridad', 'prioridad_display',
            'categoria_color', 'fecha_vencimiento', 'porcentaje_completado',
            'asignados', 'comentarios_count', 'esta_vencida', 'es_recurrente',
            'orden_subtarea'
        ]
    
    def get_asignados(self, obj):
        return [{
            'id': a.usuario.id,
            'username': a.usuario.username,
            'nombre': a.usuario.get_full_name()[:15] or a.usuario.username[:15]
        } for a in obj.asignaciones.select_related('usuario').all()[:3]]
    
    def get_comentarios_count(self, obj):
        return obj.comentarios.count()


# =============================================================================
# SERIALIZERS PARA ACCIONES
# =============================================================================

class CambiarEstadoSerializer(serializers.Serializer):
    """Serializer para cambiar estado de tarea"""
    estado = serializers.ChoiceField(choices=EstadoTarea.choices)


class CambiarColumnaSerializer(serializers.Serializer):
    """Serializer para mover tarea en Kanban"""
    columna_id = serializers.IntegerField()
    orden = serializers.IntegerField(required=False, default=0)


class AsignarTareaSerializer(serializers.Serializer):
    """Serializer para asignar tarea"""
    usuario_id = serializers.IntegerField()
    rol = serializers.ChoiceField(
        choices=RolAsignacion.choices,
        default='RESPONSABLE'
    )


class CompletarTareaSerializer(serializers.Serializer):
    """Serializer para completar tarea"""
    observaciones = serializers.CharField(required=False, allow_blank=True)
