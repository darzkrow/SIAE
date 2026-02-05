"""
Tareas Views - Task Scheduling Module API
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count
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
from .serializers import (
    CategoriaTareaSerializer,
    ColumnaKanbanSerializer,
    TareaListSerializer,
    TareaDetailSerializer,
    TareaCreateSerializer,
    TareaKanbanSerializer,
    AsignacionTareaSerializer,
    ComentarioTareaSerializer,
    ArchivoAdjuntoSerializer,
    RecordatorioTareaSerializer,
    HistorialTareaSerializer,
    CambiarEstadoSerializer,
    CambiarColumnaSerializer,
    AsignarTareaSerializer,
    CompletarTareaSerializer,
)


class CategoriaTareaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para categorías de tareas.
    
    Endpoints:
    - GET /api/tareas/categorias/ - Listar
    - POST /api/tareas/categorias/ - Crear
    - GET /api/tareas/categorias/{id}/ - Detalle
    - PUT /api/tareas/categorias/{id}/ - Actualizar
    - DELETE /api/tareas/categorias/{id}/ - Eliminar
    """
    queryset = CategoriaTarea.objects.all()
    serializer_class = CategoriaTareaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'codigo']
    ordering_fields = ['orden', 'nombre']
    ordering = ['orden', 'nombre']


class ColumnaKanbanViewSet(viewsets.ModelViewSet):
    """
    ViewSet para columnas del tablero Kanban.
    
    Endpoints:
    - GET /api/tareas/columnas/ - Listar columnas
    - POST /api/tareas/columnas/ - Crear columna
    - GET /api/tareas/columnas/{id}/ - Detalle
    - PUT /api/tareas/columnas/{id}/ - Actualizar
    - DELETE /api/tareas/columnas/{id}/ - Eliminar
    """
    queryset = ColumnaKanban.objects.all()
    serializer_class = ColumnaKanbanSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['orden']


class TareaViewSet(viewsets.ModelViewSet):
    """
    ViewSet principal para gestión de tareas.
    
    Endpoints CRUD:
    - GET /api/tareas/ - Listar tareas
    - POST /api/tareas/ - Crear tarea
    - GET /api/tareas/{id}/ - Detalle de tarea
    - PUT /api/tareas/{id}/ - Actualizar tarea
    - DELETE /api/tareas/{id}/ - Eliminar tarea
    
    Acciones especiales:
    - GET /api/tareas/mis-tareas/ - Tareas asignadas al usuario
    - GET /api/tareas/kanban/ - Vista Kanban del tablero
    - GET /api/tareas/pendientes/ - Tareas pendientes
    - GET /api/tareas/vencidas/ - Tareas vencidas
    - GET /api/tareas/dashboard/ - Resumen de tareas
    - POST /api/tareas/{id}/asignar/ - Asignar tarea
    - POST /api/tareas/{id}/completar/ - Completar tarea
    - POST /api/tareas/{id}/cambiar-estado/ - Cambiar estado
    - POST /api/tareas/{id}/mover-kanban/ - Mover en Kanban
    - GET /api/tareas/{id}/historial/ - Ver historial
    """
    queryset = Tarea.objects.select_related(
        'categoria', 'columna_kanban', 'creador', 'tarea_padre'
    ).prefetch_related(
        'asignaciones__usuario', 'comentarios', 'archivos'
    ).filter(tarea_padre__isnull=True)  # Solo tareas principales
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'categoria', 'estado', 'prioridad', 'columna_kanban',
        'es_recurrente', 'creador'
    ]
    search_fields = ['titulo', 'descripcion', 'etiquetas']
    ordering_fields = ['prioridad', 'fecha_vencimiento', 'created_at', 'estado']
    ordering = ['-prioridad', 'fecha_vencimiento']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TareaListSerializer
        elif self.action == 'create':
            return TareaCreateSerializer
        elif self.action in ['kanban', 'mis_tareas']:
            return TareaKanbanSerializer
        return TareaDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por entidad vinculada si se especifica
        content_type = self.request.query_params.get('entidad_tipo')
        object_id = self.request.query_params.get('entidad_id')
        
        if content_type and object_id:
            from django.contrib.contenttypes.models import ContentType
            try:
                ct = ContentType.objects.get(model=content_type.lower())
                queryset = queryset.filter(content_type=ct, object_id=object_id)
            except ContentType.DoesNotExist:
                pass
        
        return queryset
    
    # =========================================================================
    # LISTADOS ESPECIALES
    # =========================================================================
    
    @action(detail=False, methods=['get'], url_path='mis-tareas')
    def mis_tareas(self, request):
        """Tareas asignadas al usuario actual"""
        tareas = Tarea.objects.filter(
            asignaciones__usuario=request.user,
            estado__in=['PENDIENTE', 'EN_PROGRESO', 'EN_REVISION']
        ).select_related('categoria').distinct()
        
        serializer = TareaListSerializer(tareas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """Tareas pendientes"""
        tareas = self.queryset.filter(estado='PENDIENTE')
        serializer = TareaListSerializer(tareas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def vencidas(self, request):
        """Tareas vencidas"""
        tareas = self.queryset.filter(
            fecha_vencimiento__lt=timezone.now(),
            estado__in=['PENDIENTE', 'EN_PROGRESO']
        )
        serializer = TareaListSerializer(tareas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def kanban(self, request):
        """
        Vista Kanban: tareas agrupadas por columna.
        Devuelve las columnas con sus tareas ordenadas.
        """
        columnas = ColumnaKanban.objects.filter(activo=True).order_by('orden')
        
        # Filtros opcionales
        categoria = request.query_params.get('categoria')
        usuario = request.query_params.get('usuario')
        
        result = []
        for columna in columnas:
            tareas_query = Tarea.objects.filter(
                columna_kanban=columna,
                tarea_padre__isnull=True
            ).order_by('orden_subtarea', '-prioridad')
            
            if categoria:
                tareas_query = tareas_query.filter(categoria_id=categoria)
            if usuario:
                tareas_query = tareas_query.filter(asignaciones__usuario_id=usuario)
            
            result.append({
                'columna': ColumnaKanbanSerializer(columna).data,
                'tareas': TareaKanbanSerializer(tareas_query, many=True).data
            })
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Resumen de tareas para dashboard"""
        user = request.user
        
        # Conteos generales
        mis_tareas = Tarea.objects.filter(asignaciones__usuario=user)
        
        stats = {
            'pendientes': mis_tareas.filter(estado='PENDIENTE').count(),
            'en_progreso': mis_tareas.filter(estado='EN_PROGRESO').count(),
            'completadas_hoy': mis_tareas.filter(
                estado='COMPLETADA',
                fecha_completada__date=timezone.now().date()
            ).count(),
            'vencidas': mis_tareas.filter(
                fecha_vencimiento__lt=timezone.now(),
                estado__in=['PENDIENTE', 'EN_PROGRESO']
            ).count(),
            'por_vencer': mis_tareas.filter(
                fecha_vencimiento__gte=timezone.now(),
                fecha_vencimiento__lte=timezone.now() + timezone.timedelta(days=3),
                estado__in=['PENDIENTE', 'EN_PROGRESO']
            ).count(),
        }
        
        # Tareas urgentes
        urgentes = mis_tareas.filter(
            prioridad='URGENTE',
            estado__in=['PENDIENTE', 'EN_PROGRESO']
        ).order_by('fecha_vencimiento')[:5]
        
        # Próximas tareas
        proximas = mis_tareas.filter(
            estado__in=['PENDIENTE', 'EN_PROGRESO'],
            fecha_vencimiento__gte=timezone.now()
        ).order_by('fecha_vencimiento')[:10]
        
        return Response({
            'stats': stats,
            'urgentes': TareaListSerializer(urgentes, many=True).data,
            'proximas': TareaListSerializer(proximas, many=True).data,
        })
    
    # =========================================================================
    # ACCIONES SOBRE TAREAS
    # =========================================================================
    
    @action(detail=True, methods=['post'])
    def asignar(self, request, pk=None):
        """Asignar tarea a un usuario"""
        tarea = self.get_object()
        serializer = AsignarTareaSerializer(data=request.data)
        
        if serializer.is_valid():
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            try:
                usuario = User.objects.get(pk=serializer.validated_data['usuario_id'])
            except User.DoesNotExist:
                return Response(
                    {'error': 'Usuario no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            asignacion, created = AsignacionTarea.objects.get_or_create(
                tarea=tarea,
                usuario=usuario,
                defaults={
                    'rol': serializer.validated_data['rol'],
                    'asignado_por': request.user
                }
            )
            
            if not created:
                asignacion.rol = serializer.validated_data['rol']
                asignacion.save()
            
            return Response(AsignacionTareaSerializer(asignacion).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        """Marcar tarea como completada"""
        tarea = self.get_object()
        serializer = CompletarTareaSerializer(data=request.data)
        
        if serializer.is_valid():
            tarea.completar(usuario=request.user)
            
            if serializer.validated_data.get('observaciones'):
                ComentarioTarea.objects.create(
                    tarea=tarea,
                    autor=request.user,
                    contenido=f"Completada: {serializer.validated_data['observaciones']}"
                )
            
            return Response(TareaDetailSerializer(tarea).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='cambiar-estado')
    def cambiar_estado(self, request, pk=None):
        """Cambiar estado de la tarea"""
        tarea = self.get_object()
        serializer = CambiarEstadoSerializer(data=request.data)
        
        if serializer.is_valid():
            estado_anterior = tarea.estado
            nuevo_estado = serializer.validated_data['estado']
            
            tarea.estado = nuevo_estado
            
            if nuevo_estado == 'COMPLETADA':
                tarea.fecha_completada = timezone.now()
                tarea.porcentaje_completado = 100
            
            tarea.save()
            
            # Registrar en historial
            HistorialTarea.objects.create(
                tarea=tarea,
                usuario=request.user,
                accion='ESTADO_CAMBIADO',
                descripcion=f'Estado cambiado de {estado_anterior} a {nuevo_estado}',
                datos_anteriores={'estado': estado_anterior},
                datos_nuevos={'estado': nuevo_estado}
            )
            
            return Response(TareaDetailSerializer(tarea).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='mover-kanban')
    def mover_kanban(self, request, pk=None):
        """Mover tarea a otra columna del Kanban"""
        tarea = self.get_object()
        serializer = CambiarColumnaSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                columna = ColumnaKanban.objects.get(
                    pk=serializer.validated_data['columna_id']
                )
            except ColumnaKanban.DoesNotExist:
                return Response(
                    {'error': 'Columna no encontrada'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            columna_anterior = tarea.columna_kanban
            tarea.columna_kanban = columna
            tarea.orden_subtarea = serializer.validated_data.get('orden', 0)
            
            # Actualizar estado según tipo de columna
            if columna.tipo == 'FIN':
                tarea.estado = 'COMPLETADA'
                tarea.fecha_completada = timezone.now()
                tarea.porcentaje_completado = 100
            elif columna.tipo == 'INICIO':
                tarea.estado = 'PENDIENTE'
            elif columna.tipo == 'PROGRESO':
                if tarea.estado not in ['EN_PROGRESO', 'EN_REVISION']:
                    tarea.estado = 'EN_PROGRESO'
            
            tarea.save()
            
            # Registrar movimiento
            HistorialTarea.objects.create(
                tarea=tarea,
                usuario=request.user,
                accion='ESTADO_CAMBIADO',
                descripcion=f'Movida a columna: {columna.nombre}',
                datos_anteriores={
                    'columna': columna_anterior.nombre if columna_anterior else None
                },
                datos_nuevos={'columna': columna.nombre}
            )
            
            return Response(TareaKanbanSerializer(tarea).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def historial(self, request, pk=None):
        """Ver historial de la tarea"""
        tarea = self.get_object()
        historial = tarea.historial.select_related('usuario').all()
        serializer = HistorialTareaSerializer(historial, many=True)
        return Response(serializer.data)


class AsignacionTareaViewSet(viewsets.ModelViewSet):
    """ViewSet para asignaciones de tareas"""
    queryset = AsignacionTarea.objects.select_related('tarea', 'usuario', 'asignado_por')
    serializer_class = AsignacionTareaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['tarea', 'usuario', 'rol']


class ComentarioTareaViewSet(viewsets.ModelViewSet):
    """ViewSet para comentarios"""
    queryset = ComentarioTarea.objects.select_related('tarea', 'autor')
    serializer_class = ComentarioTareaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['tarea']
    ordering = ['-created_at']


class ArchivoAdjuntoViewSet(viewsets.ModelViewSet):
    """ViewSet para archivos adjuntos"""
    queryset = ArchivoAdjunto.objects.select_related('tarea', 'subido_por')
    serializer_class = ArchivoAdjuntoSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['tarea']


class RecordatorioTareaViewSet(viewsets.ModelViewSet):
    """ViewSet para recordatorios"""
    queryset = RecordatorioTarea.objects.select_related('tarea', 'usuario')
    serializer_class = RecordatorioTareaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['tarea', 'usuario', 'enviado', 'tipo']
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """Recordatorios pendientes de enviar"""
        recordatorios = self.queryset.filter(
            enviado=False,
            fecha_recordatorio__lte=timezone.now()
        )
        serializer = self.get_serializer(recordatorios, many=True)
        return Response(serializer.data)
