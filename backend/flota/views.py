"""
Flota Views - Fleet Management API ViewSets
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count, Sum
from .models import (
    TipoVehiculo,
    Vehiculo,
    DocumentoVehiculo,
    MantenimientoVehiculo,
    AsignacionVehiculo,
    RegistroCombustible,
)
from .choices import TipoVehiculoChoices, EstadoVehiculo
from .serializers import (
    TipoVehiculoSerializer,
    VehiculoListSerializer,
    VehiculoDetailSerializer,
    VehiculoCreateSerializer,
    DocumentoVehiculoSerializer,
    MantenimientoVehiculoSerializer,
    AsignacionVehiculoSerializer,
    RegistroCombustibleSerializer,
    FinalizarAsignacionSerializer,
    ActualizarKilometrajeSerializer,
    ActualizarHorasMotorSerializer,
    CompletarMantenimientoSerializer,
)


class TipoVehiculoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para catálogo de tipos de vehículos.
    
    Endpoints:
    - GET /api/flota/tipos/ - Listar tipos
    - POST /api/flota/tipos/ - Crear tipo
    - GET /api/flota/tipos/{id}/ - Detalle
    - PUT /api/flota/tipos/{id}/ - Actualizar
    - DELETE /api/flota/tipos/{id}/ - Eliminar
    - GET /api/flota/tipos/por-categoria/ - Agrupados por categoría
    """
    queryset = TipoVehiculo.objects.all()
    serializer_class = TipoVehiculoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categoria', 'activo', 'requiere_licencia_especial']
    search_fields = ['nombre', 'codigo', 'descripcion']
    ordering_fields = ['nombre', 'categoria', 'created_at']
    ordering = ['categoria', 'nombre']
    
    @action(detail=False, methods=['get'])
    def por_categoria(self, request):
        """Obtener tipos agrupados por categoría"""
        result = {}
        for cat_code, cat_name in TipoVehiculoChoices.choices:
            tipos = TipoVehiculo.objects.filter(categoria=cat_code, activo=True)
            result[cat_code] = {
                'nombre': cat_name,
                'tipos': TipoVehiculoSerializer(tipos, many=True).data
            }
        return Response(result)


class VehiculoViewSet(viewsets.ModelViewSet):
    """
    ViewSet principal para gestión de vehículos.
    
    Endpoints:
    - GET /api/flota/vehiculos/ - Listar vehículos
    - POST /api/flota/vehiculos/ - Crear vehículo
    - GET /api/flota/vehiculos/{id}/ - Detalle
    - PUT /api/flota/vehiculos/{id}/ - Actualizar
    - DELETE /api/flota/vehiculos/{id}/ - Eliminar
    
    Acciones especiales:
    - POST /api/flota/vehiculos/{id}/asignar/ - Asignar a usuario
    - POST /api/flota/vehiculos/{id}/actualizar-km/ - Actualizar kilometraje
    - POST /api/flota/vehiculos/{id}/actualizar-horas/ - Actualizar horas motor
    - GET /api/flota/vehiculos/{id}/historial/ - Historial completo
    - GET /api/flota/vehiculos/requieren-mantenimiento/ - Vehículos que necesitan mantenimiento
    - GET /api/flota/vehiculos/disponibles/ - Vehículos disponibles
    - GET /api/flota/vehiculos/estadisticas/ - Estadísticas de flota
    """
    queryset = Vehiculo.objects.select_related(
        'tipo_vehiculo', 'unidad_organizacional', 'almacen_actual',
        'responsable_actual', 'proveedor', 'creado_por'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'tipo_vehiculo', 'tipo_vehiculo__categoria', 'estado',
        'unidad_organizacional', 'almacen_actual', 'responsable_actual',
        'activo', 'tipo_combustible'
    ]
    search_fields = ['codigo', 'placa', 'serial_motor', 'serial_carroceria', 'marca', 'modelo']
    ordering_fields = ['codigo', 'marca', 'modelo', 'año', 'kilometraje_actual', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return VehiculoListSerializer
        elif self.action == 'create':
            return VehiculoCreateSerializer
        return VehiculoDetailSerializer
    
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """Listar vehículos disponibles"""
        vehiculos = self.queryset.filter(estado='DISPONIBLE', activo=True)
        
        # Filtrar por tipo si se especifica
        tipo = request.query_params.get('tipo')
        if tipo:
            vehiculos = vehiculos.filter(tipo_vehiculo_id=tipo)
        
        # Filtrar por categoría si se especifica
        categoria = request.query_params.get('categoria')
        if categoria:
            vehiculos = vehiculos.filter(tipo_vehiculo__categoria=categoria)
        
        serializer = VehiculoListSerializer(vehiculos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def requieren_mantenimiento(self, request):
        """Listar vehículos que requieren mantenimiento"""
        vehiculos = []
        for v in self.queryset.filter(activo=True):
            if v.necesita_mantenimiento():
                vehiculos.append(v)
        
        serializer = VehiculoListSerializer(vehiculos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas generales de la flota"""
        vehiculos = self.queryset.filter(activo=True)
        
        # Por estado
        por_estado = {}
        for estado_code, estado_name in EstadoVehiculo.choices:
            count = vehiculos.filter(estado=estado_code).count()
            if count > 0:
                por_estado[estado_code] = {
                    'nombre': estado_name,
                    'cantidad': count
                }
        
        # Por categoría
        por_categoria = {}
        for cat_code, cat_name in TipoVehiculoChoices.choices:
            count = vehiculos.filter(tipo_vehiculo__categoria=cat_code).count()
            if count > 0:
                por_categoria[cat_code] = {
                    'nombre': cat_name,
                    'cantidad': count
                }
        
        # Mantenimientos pendientes
        mantenimientos_pendientes = MantenimientoVehiculo.objects.filter(
            estado='PROGRAMADO'
        ).count()
        
        # Documentos por vencer (30 días)
        from datetime import timedelta
        fecha_limite = timezone.now().date() + timedelta(days=30)
        documentos_por_vencer = DocumentoVehiculo.objects.filter(
            fecha_vencimiento__lte=fecha_limite,
            fecha_vencimiento__gte=timezone.now().date()
        ).count()
        
        return Response({
            'total_vehiculos': vehiculos.count(),
            'por_estado': por_estado,
            'por_categoria': por_categoria,
            'mantenimientos_pendientes': mantenimientos_pendientes,
            'documentos_por_vencer': documentos_por_vencer,
        })
    
    @action(detail=True, methods=['post'])
    def asignar(self, request, pk=None):
        """Asignar vehículo a un usuario"""
        vehiculo = self.get_object()
        
        if vehiculo.estado not in ['DISPONIBLE', 'RESERVADO']:
            return Response(
                {'error': 'El vehículo no está disponible para asignación'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = AsignacionVehiculoSerializer(
            data={**request.data, 'vehiculo': vehiculo.id},
            context={'request': request}
        )
        
        if serializer.is_valid():
            asignacion = serializer.save()
            return Response(
                AsignacionVehiculoSerializer(asignacion).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='actualizar-km')
    def actualizar_km(self, request, pk=None):
        """Actualizar kilometraje del vehículo"""
        vehiculo = self.get_object()
        serializer = ActualizarKilometrajeSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                vehiculo.actualizar_kilometraje(
                    serializer.validated_data['kilometraje'],
                    usuario=request.user
                )
                return Response({
                    'mensaje': 'Kilometraje actualizado',
                    'kilometraje_actual': vehiculo.kilometraje_actual,
                    'necesita_mantenimiento': vehiculo.necesita_mantenimiento()
                })
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='actualizar-horas')
    def actualizar_horas(self, request, pk=None):
        """Actualizar horas de motor del vehículo"""
        vehiculo = self.get_object()
        serializer = ActualizarHorasMotorSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                vehiculo.actualizar_horas_motor(
                    serializer.validated_data['horas_motor'],
                    usuario=request.user
                )
                return Response({
                    'mensaje': 'Horas de motor actualizadas',
                    'horas_motor_actual': vehiculo.horas_motor_actual,
                    'necesita_mantenimiento': vehiculo.necesita_mantenimiento()
                })
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def historial(self, request, pk=None):
        """Obtener historial completo del vehículo"""
        vehiculo = self.get_object()
        
        return Response({
            'vehiculo': VehiculoDetailSerializer(vehiculo).data,
            'documentos': DocumentoVehiculoSerializer(
                vehiculo.documentos.all(), many=True
            ).data,
            'mantenimientos': MantenimientoVehiculoSerializer(
                vehiculo.mantenimientos.all()[:20], many=True
            ).data,
            'asignaciones': AsignacionVehiculoSerializer(
                vehiculo.asignaciones.all()[:20], many=True
            ).data,
            'combustible': RegistroCombustibleSerializer(
                vehiculo.registros_combustible.all()[:50], many=True
            ).data,
        })


class DocumentoVehiculoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para documentos de vehículos.
    
    Endpoints:
    - GET /api/flota/documentos/ - Listar documentos
    - POST /api/flota/documentos/ - Crear documento
    - GET /api/flota/documentos/{id}/ - Detalle
    - PUT /api/flota/documentos/{id}/ - Actualizar
    - DELETE /api/flota/documentos/{id}/ - Eliminar
    - GET /api/flota/documentos/proximos-vencer/ - Por vencer
    - GET /api/flota/documentos/vencidos/ - Vencidos
    """
    queryset = DocumentoVehiculo.objects.select_related('vehiculo', 'subido_por').all()
    serializer_class = DocumentoVehiculoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['vehiculo', 'tipo_documento', 'alertar_vencimiento']
    search_fields = ['nombre', 'numero_documento', 'vehiculo__codigo', 'vehiculo__placa']
    ordering_fields = ['fecha_vencimiento', 'fecha_emision', 'created_at']
    ordering = ['fecha_vencimiento']
    
    @action(detail=False, methods=['get'], url_path='proximos-vencer')
    def proximos_vencer(self, request):
        """Documentos próximos a vencer"""
        dias = int(request.query_params.get('dias', 30))
        from datetime import timedelta
        
        fecha_limite = timezone.now().date() + timedelta(days=dias)
        documentos = self.queryset.filter(
            fecha_vencimiento__lte=fecha_limite,
            fecha_vencimiento__gte=timezone.now().date()
        ).order_by('fecha_vencimiento')
        
        serializer = self.get_serializer(documentos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def vencidos(self, request):
        """Documentos vencidos"""
        documentos = self.queryset.filter(
            fecha_vencimiento__lt=timezone.now().date()
        ).order_by('fecha_vencimiento')
        
        serializer = self.get_serializer(documentos, many=True)
        return Response(serializer.data)


class MantenimientoVehiculoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para mantenimientos de vehículos.
    
    Endpoints:
    - GET /api/flota/mantenimientos/ - Listar
    - POST /api/flota/mantenimientos/ - Crear (programar)
    - GET /api/flota/mantenimientos/{id}/ - Detalle
    - PUT /api/flota/mantenimientos/{id}/ - Actualizar
    - DELETE /api/flota/mantenimientos/{id}/ - Eliminar
    - POST /api/flota/mantenimientos/{id}/iniciar/ - Iniciar mantenimiento
    - POST /api/flota/mantenimientos/{id}/completar/ - Completar mantenimiento
    - POST /api/flota/mantenimientos/{id}/cancelar/ - Cancelar
    - GET /api/flota/mantenimientos/programados/ - Programados
    - GET /api/flota/mantenimientos/en-proceso/ - En proceso
    """
    queryset = MantenimientoVehiculo.objects.select_related(
        'vehiculo', 'proveedor_servicio', 'solicitado_por', 'realizado_por'
    ).all()
    serializer_class = MantenimientoVehiculoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['vehiculo', 'tipo_mantenimiento', 'estado', 'proveedor_servicio']
    search_fields = ['vehiculo__codigo', 'vehiculo__placa', 'descripcion']
    ordering_fields = ['fecha_programada', 'fecha_inicio', 'costo_total', 'created_at']
    ordering = ['-fecha_programada']
    
    @action(detail=False, methods=['get'])
    def programados(self, request):
        """Mantenimientos programados"""
        mantenimientos = self.queryset.filter(estado='PROGRAMADO')
        serializer = self.get_serializer(mantenimientos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='en-proceso')
    def en_proceso(self, request):
        """Mantenimientos en proceso"""
        mantenimientos = self.queryset.filter(estado='EN_PROCESO')
        serializer = self.get_serializer(mantenimientos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def iniciar(self, request, pk=None):
        """Iniciar un mantenimiento programado"""
        mantenimiento = self.get_object()
        
        if mantenimiento.estado != 'PROGRAMADO':
            return Response(
                {'error': 'Solo se pueden iniciar mantenimientos programados'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        mantenimiento.estado = 'EN_PROCESO'
        mantenimiento.fecha_inicio = timezone.now()
        mantenimiento.kilometraje_servicio = mantenimiento.vehiculo.kilometraje_actual
        mantenimiento.horas_motor_servicio = mantenimiento.vehiculo.horas_motor_actual
        mantenimiento.save()
        
        # Actualizar estado del vehículo
        mantenimiento.vehiculo.estado = 'MANTENIMIENTO'
        mantenimiento.vehiculo.save()
        
        return Response(self.get_serializer(mantenimiento).data)
    
    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        """Completar un mantenimiento"""
        mantenimiento = self.get_object()
        
        if mantenimiento.estado != 'EN_PROCESO':
            return Response(
                {'error': 'Solo se pueden completar mantenimientos en proceso'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CompletarMantenimientoSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            mantenimiento.estado = 'COMPLETADO'
            mantenimiento.fecha_fin = timezone.now()
            mantenimiento.trabajos_realizados = data['trabajos_realizados']
            mantenimiento.repuestos_utilizados = data.get('repuestos_utilizados', '')
            mantenimiento.costo_mano_obra = data['costo_mano_obra']
            mantenimiento.costo_repuestos = data.get('costo_repuestos', 0)
            mantenimiento.observaciones = data.get('observaciones', '')
            mantenimiento.realizado_por = request.user
            mantenimiento.save()
            
            # Restaurar estado del vehículo
            mantenimiento.vehiculo.estado = 'DISPONIBLE'
            mantenimiento.vehiculo.save()
            
            return Response(self.get_serializer(mantenimiento).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancelar un mantenimiento"""
        mantenimiento = self.get_object()
        
        if mantenimiento.estado in ['COMPLETADO', 'CANCELADO']:
            return Response(
                {'error': 'No se puede cancelar este mantenimiento'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        mantenimiento.estado = 'CANCELADO'
        mantenimiento.observaciones = f"{mantenimiento.observaciones}\n\nCancelado: {request.data.get('motivo', 'Sin especificar')}"
        mantenimiento.save()
        
        # Restaurar estado del vehículo si estaba en mantenimiento
        if mantenimiento.vehiculo.estado == 'MANTENIMIENTO':
            mantenimiento.vehiculo.estado = 'DISPONIBLE'
            mantenimiento.vehiculo.save()
        
        return Response(self.get_serializer(mantenimiento).data)


class AsignacionVehiculoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para asignaciones de vehículos.
    
    Endpoints:
    - GET /api/flota/asignaciones/ - Listar
    - POST /api/flota/asignaciones/ - Crear
    - GET /api/flota/asignaciones/{id}/ - Detalle
    - PUT /api/flota/asignaciones/{id}/ - Actualizar
    - DELETE /api/flota/asignaciones/{id}/ - Eliminar
    - POST /api/flota/asignaciones/{id}/finalizar/ - Finalizar
    - GET /api/flota/asignaciones/activas/ - Activas
    """
    queryset = AsignacionVehiculo.objects.select_related(
        'vehiculo', 'usuario_asignado', 'unidad_destino', 'asignado_por'
    ).all()
    serializer_class = AsignacionVehiculoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['vehiculo', 'usuario_asignado', 'unidad_destino', 'tipo_asignacion', 'activa']
    search_fields = ['vehiculo__codigo', 'vehiculo__placa', 'motivo']
    ordering_fields = ['fecha_inicio', 'fecha_fin', 'created_at']
    ordering = ['-fecha_inicio']
    
    @action(detail=False, methods=['get'])
    def activas(self, request):
        """Asignaciones activas"""
        asignaciones = self.queryset.filter(activa=True)
        serializer = self.get_serializer(asignaciones, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def finalizar(self, request, pk=None):
        """Finalizar una asignación"""
        asignacion = self.get_object()
        
        if not asignacion.activa:
            return Response(
                {'error': 'La asignación ya está finalizada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = FinalizarAsignacionSerializer(data=request.data)
        if serializer.is_valid():
            asignacion.finalizar_asignacion(
                km_final=serializer.validated_data.get('kilometraje_final'),
                horas_final=serializer.validated_data.get('horas_motor_final'),
                observaciones=serializer.validated_data.get('observaciones', '')
            )
            return Response(self.get_serializer(asignacion).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegistroCombustibleViewSet(viewsets.ModelViewSet):
    """
    ViewSet para registros de combustible.
    
    Endpoints:
    - GET /api/flota/combustible/ - Listar
    - POST /api/flota/combustible/ - Crear
    - GET /api/flota/combustible/{id}/ - Detalle
    - PUT /api/flota/combustible/{id}/ - Actualizar
    - DELETE /api/flota/combustible/{id}/ - Eliminar
    - GET /api/flota/combustible/resumen/ - Resumen de consumo
    """
    queryset = RegistroCombustible.objects.select_related(
        'vehiculo', 'registrado_por', 'conductor'
    ).all()
    serializer_class = RegistroCombustibleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['vehiculo', 'tipo_combustible', 'tanque_lleno']
    search_fields = ['vehiculo__codigo', 'vehiculo__placa', 'estacion_servicio']
    ordering_fields = ['fecha', 'litros', 'costo', 'created_at']
    ordering = ['-fecha']
    
    @action(detail=False, methods=['get'])
    def resumen(self, request):
        """Resumen de consumo de combustible"""
        vehiculo_id = request.query_params.get('vehiculo')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        registros = self.queryset
        
        if vehiculo_id:
            registros = registros.filter(vehiculo_id=vehiculo_id)
        if fecha_inicio:
            registros = registros.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            registros = registros.filter(fecha__lte=fecha_fin)
        
        totales = registros.aggregate(
            total_litros=Sum('litros'),
            total_costo=Sum('costo'),
            total_registros=Count('id')
        )
        
        return Response({
            'total_litros': totales['total_litros'] or 0,
            'total_costo': totales['total_costo'] or 0,
            'total_registros': totales['total_registros'] or 0,
        })
