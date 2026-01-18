from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, F, Count
from decimal import Decimal
from inventario.models import Acueducto
# Importar permisos existentes
from inventario.permissions import IsAdminOrReadOnly, IsAdminOrSameSucursal
from inventario.serializers import AcueductoSerializer
# Imports de modelos y serializers
from inventario.models import (
    OrganizacionCentral, Sucursal, Acueducto,
    Category, UnitOfMeasure, Supplier,
    ChemicalProduct, Pipe, PumpAndMotor, Accessory,
    StockChemical, StockPipe, StockPumpAndMotor, StockAccessory,
    FichaTecnicaMotor, RegistroMantenimiento, OrdenCompra
)
from django.contrib.auth import get_user_model
User = get_user_model()
from inventario.serializers import (
    CategorySerializer, UnitOfMeasureSerializer, SupplierSerializer,
    ChemicalProductSerializer, PipeSerializer,
    PumpAndMotorSerializer, AccessorySerializer,
    StockChemicalSerializer, StockPipeSerializer,
    StockPumpAndMotorSerializer, StockAccessorySerializer,
    ChemicalProductListSerializer, PipeListSerializer,
    PumpAndMotorListSerializer, AccessoryListSerializer,
    MovimientoInventarioSerializer,
    OrganizacionCentralSerializer, SucursalSerializer, UserSerializer,
    AlertaSerializer, NotificacionSerializer,
    FichaTecnicaMotorSerializer, RegistroMantenimientoSerializer, OrdenCompraSerializer
)


# ============================================================================
# VIEWSETS DE MODELOS ORGANIZACIONALES
# ============================================================================

class OrganizacionCentralViewSet(viewsets.ModelViewSet):
    """ViewSet para organizaciones centrales."""
    queryset = OrganizacionCentral.objects.all()
    serializer_class = OrganizacionCentralSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ['nombre', 'rif']

class SucursalViewSet(viewsets.ModelViewSet):
    """ViewSet para sucursales."""
    queryset = Sucursal.objects.select_related('organizacion_central').all()
    serializer_class = SucursalSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['organizacion_central']
    search_fields = ['nombre', 'codigo']

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de usuarios."""
    queryset = User.objects.select_related('sucursal').all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated] # Solo ADMIN debería acceder a todo, filtrar en get_queryset
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role', 'sucursal', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    def get_queryset(self):
        user = self.request.user
        if user.role == user.ROLE_ADMIN:
            return super().get_queryset()
        return super().get_queryset().filter(id=user.id)


# ============================================================================
# VIEWSETS DE MODELOS AUXILIARES
# ============================================================================

class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet para categorías de productos."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo']
    search_fields = ['nombre', 'codigo', 'descripcion']
    ordering_fields = ['orden', 'nombre']
    ordering = ['orden', 'nombre']


class UnitOfMeasureViewSet(viewsets.ModelViewSet):
    """ViewSet para unidades de medida."""
    queryset = UnitOfMeasure.objects.all()
    serializer_class = UnitOfMeasureSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'activo']
    search_fields = ['nombre', 'simbolo']
    ordering_fields = ['tipo', 'nombre']
    ordering = ['tipo', 'nombre']


class SupplierViewSet(viewsets.ModelViewSet):
    """ViewSet para proveedores."""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo']
    search_fields = ['nombre', 'rif', 'codigo', 'contacto_nombre', 'email']
    ordering_fields = ['nombre', 'creado_en']
    ordering = ['nombre']


class AcueductoViewSet(viewsets.ModelViewSet):
    """ViewSet para acueductos."""

    queryset = Acueducto.objects.all()
    
    def get_serializer_class(self):
        
        return AcueductoSerializer
        
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sucursal']
    search_fields = ['nombre', 'ubicacion']
    ordering_fields = ['nombre']
    ordering = ['nombre']


# ============================================================================
# VIEWSETS DE PRODUCTOS
# ============================================================================

class ChemicalProductViewSet(viewsets.ModelViewSet):
    """ViewSet para productos químicos."""
    queryset = ChemicalProduct.objects.select_related(
        'categoria', 'unidad_medida', 'proveedor'
    ).all()
    serializer_class = ChemicalProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'categoria', 'activo', 'es_peligroso',
        'nivel_peligrosidad', 'presentacion', 'proveedor'
    ]
    search_fields = ['sku', 'nombre', 'descripcion', 'numero_un']
    ordering_fields = ['sku', 'nombre', 'stock_actual', 'precio_unitario', 'fecha_caducidad']
    ordering = ['sku']
    
    def get_serializer_class(self):
        """Usar serializer simplificado para listados."""
        if self.action == 'list':
            return ChemicalProductListSerializer
        return ChemicalProductSerializer
    
    @action(detail=False, methods=['get'])
    def stock_bajo(self, request):
        """Productos químicos con stock bajo."""
        queryset = self.get_queryset().filter(
            stock_actual__lte=F('stock_minimo')
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def peligrosos(self, request):
        """Productos químicos peligrosos."""
        queryset = self.get_queryset().filter(es_peligroso=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def proximos_vencer(self, request):
        """Productos químicos próximos a vencer (30 días)."""
        from datetime import timedelta
        from django.utils import timezone
        
        fecha_limite = timezone.now().date() + timedelta(days=30)
        queryset = self.get_queryset().filter(
            fecha_caducidad__lte=fecha_limite,
            fecha_caducidad__gte=timezone.now().date()
        ).order_by('fecha_caducidad')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Historial de movimientos para este químico."""
        from inventario.models import MovimientoInventario
        from django.contrib.contenttypes.models import ContentType
        
        ct = ContentType.objects.get_for_model(ChemicalProduct)
        movimientos = MovimientoInventario.objects.filter(
            content_type=ct, 
            object_id=pk
        ).order_by('-fecha_movimiento')
        
        from inventario.serializers import MovimientoInventarioSerializer
        serializer = MovimientoInventarioSerializer(movimientos, many=True)
        return Response(serializer.data)


class PipeViewSet(viewsets.ModelViewSet):
    """ViewSet para tuberías."""
    queryset = Pipe.objects.select_related(
        'categoria', 'unidad_medida', 'proveedor'
    ).all()
    serializer_class = PipeSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'categoria', 'activo', 'material', 'tipo_uso',
        'presion_nominal', 'tipo_union', 'proveedor'
    ]
    search_fields = ['sku', 'nombre', 'descripcion']
    ordering_fields = ['sku', 'nombre', 'diametro_nominal', 'stock_actual', 'precio_unitario']
    ordering = ['sku']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PipeListSerializer
        return PipeSerializer
    
    @action(detail=False, methods=['get'])
    def by_diameter(self, request):
        """Agrupar tuberías por diámetro."""
        diametro = request.query_params.get('diametro')
        if not diametro:
            return Response(
                {'error': 'Parámetro diámetro requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(diametro_nominal=diametro)
        serializer = self.get_serializer(queryset, many=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Historial de movimientos para esta tubería."""
        from inventario.models import MovimientoInventario
        from django.contrib.contenttypes.models import ContentType
        
        ct = ContentType.objects.get_for_model(Pipe)
        movimientos = MovimientoInventario.objects.filter(
            content_type=ct, 
            object_id=pk
        ).order_by('-fecha_movimiento')
        
        from inventario.serializers import MovimientoInventarioSerializer
        serializer = MovimientoInventarioSerializer(movimientos, many=True)
        return Response(serializer.data)


class PumpAndMotorViewSet(viewsets.ModelViewSet):
    """ViewSet para bombas y motores."""
    queryset = PumpAndMotor.objects.select_related(
        'categoria', 'unidad_medida', 'proveedor'
    ).all()
    serializer_class = PumpAndMotorSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'categoria', 'activo', 'tipo_equipo', 'marca',
        'fases', 'voltaje', 'proveedor'
    ]
    search_fields = ['sku', 'nombre', 'descripcion', 'numero_serie', 'marca', 'modelo']
    ordering_fields = ['sku', 'nombre', 'potencia_hp', 'stock_actual', 'precio_unitario']
    ordering = ['sku']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PumpAndMotorListSerializer
        return PumpAndMotorSerializer
    
    @action(detail=False, methods=['get'])
    def by_power_range(self, request):
        """Bombas por rango de potencia."""
        min_hp = request.query_params.get('min_hp', 0)
        max_hp = request.query_params.get('max_hp', 999)
        
        queryset = self.get_queryset().filter(
            potencia_hp__gte=Decimal(min_hp),
            potencia_hp__lte=Decimal(max_hp)
        )
        serializer = self.get_serializer(queryset, many=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Historial de movimientos para esta bomba/motor."""
        from inventario.models import MovimientoInventario
        from django.contrib.contenttypes.models import ContentType
        
        ct = ContentType.objects.get_for_model(PumpAndMotor)
        movimientos = MovimientoInventario.objects.filter(
            content_type=ct, 
            object_id=pk
        ).order_by('-fecha_movimiento')
        
        from inventario.serializers import MovimientoInventarioSerializer
        serializer = MovimientoInventarioSerializer(movimientos, many=True)
        return Response(serializer.data)


class AccessoryViewSet(viewsets.ModelViewSet):
    """ViewSet para accesorios."""
    queryset = Accessory.objects.select_related(
        'categoria', 'unidad_medida', 'proveedor'
    ).all()
    serializer_class = AccessorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'categoria', 'activo', 'tipo_accesorio', 'subtipo',
        'tipo_conexion', 'material', 'proveedor'
    ]
    search_fields = ['sku', 'nombre', 'descripcion']
    ordering_fields = ['sku', 'nombre', 'stock_actual', 'precio_unitario']
    ordering = ['sku']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AccessoryListSerializer
        return AccessorySerializer
    
    @action(detail=False, methods=['get'])
    def valvulas(self, request):
        """Filtrar solo válvulas."""
        queryset = self.get_queryset().filter(tipo_accesorio='VALVULA')
        serializer = self.get_serializer(queryset, many=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Historial de movimientos para este accesorio."""
        from inventario.models import MovimientoInventario
        from django.contrib.contenttypes.models import ContentType
        
        ct = ContentType.objects.get_for_model(Accessory)
        movimientos = MovimientoInventario.objects.filter(
            content_type=ct, 
            object_id=pk
        ).order_by('-fecha_movimiento')
        
        from inventario.serializers import MovimientoInventarioSerializer
        serializer = MovimientoInventarioSerializer(movimientos, many=True)
        return Response(serializer.data)


# ============================================================================
# VIEWSETS DE STOCK
# ============================================================================

class StockChemicalViewSet(viewsets.ModelViewSet):
    """ViewSet para stock de químicos."""
    queryset = StockChemical.objects.select_related(
        'producto', 'producto__categoria', 'acueducto', 'acueducto__sucursal'
    ).all()
    serializer_class = StockChemicalSerializer
    permission_classes = [IsAdminOrSameSucursal]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['producto', 'acueducto']
    search_fields = ['producto__nombre', 'producto__sku', 'lote', 'ubicacion_fisica']
    ordering = ['producto__sku']
    
    def get_queryset(self):
        """Filtrar por sucursal del usuario."""
        queryset = super().get_queryset()  # Implementar lógica similar a StockTuberiaViewSet
        user = self.request.user
        
        if user.role == user.ROLE_ADMIN:
            return queryset
        
        if user.sucursal:
            return queryset.filter(acueducto__sucursal=user.sucursal)
        
        return queryset.none()


class StockPipeViewSet(viewsets.ModelViewSet):
    """ViewSet para stock de tuberías."""
    queryset = StockPipe.objects.select_related(
        'producto', 'producto__categoria', 'acueducto', 'acueducto__sucursal'
    ).all()
    serializer_class = StockPipeSerializer
    permission_classes = [IsAdminOrSameSucursal]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['producto', 'acueducto']
    search_fields = ['producto__nombre', 'producto__sku', 'ubicacion_fisica']
    ordering = ['producto__sku']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.role == user.ROLE_ADMIN:
            return queryset
        
        if user.sucursal:
            return queryset.filter(acueducto__sucursal=user.sucursal)
        
        return queryset.none()


class StockPumpAndMotorViewSet(viewsets.ModelViewSet):
    """ViewSet para stock de bombas/motores."""
    queryset = StockPumpAndMotor.objects.select_related(
        'producto', 'producto__categoria', 'acueducto', 'acueducto__sucursal'
    ).all()
    serializer_class = StockPumpAndMotorSerializer
    permission_classes = [IsAdminOrSameSucursal]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['producto', 'acueducto', 'estado_operativo']
    search_fields = ['producto__nombre', 'producto__numero_serie', 'ubicacion_fisica']
    ordering = ['producto__numero_serie']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.role == user.ROLE_ADMIN:
            return queryset
        
        if user.sucursal:
            return queryset.filter(acueducto__sucursal=user.sucursal)
        
        return queryset.none()


class StockAccessoryViewSet(viewsets.ModelViewSet):
    """ViewSet para stock de accesorios."""
    queryset = StockAccessory.objects.select_related(
        'producto', 'producto__categoria', 'acueducto', 'acueducto__sucursal'
    ).all()
    serializer_class = StockAccessorySerializer
    permission_classes = [IsAdminOrSameSucursal]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['producto', 'acueducto']
    search_fields = ['producto__nombre', 'producto__sku', 'ubicacion_fisica']
    ordering = ['producto__sku']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.role == user.ROLE_ADMIN:
            return queryset
        
        if user.sucursal:
            return queryset.filter(acueducto__sucursal=user.sucursal)
        
        return queryset.none()



# ============================================================================
# VIEWSET DE MOVIMIENTOS
# ============================================================================

class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    """ViewSet para movimientos de inventario."""
    # queryset se define dinámicamente o se importa
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo_movimiento', 'acueducto_origen', 'acueducto_destino']
    search_fields = ['razon']  # producto__sku no compatible con GFK en SearchFilter
    ordering = ['-fecha_movimiento']

    def get_queryset(self):
        from inventario.models import MovimientoInventario
        return MovimientoInventario.objects.all().select_related(
            'acueducto_origen', 'acueducto_destino', 'creado_por', 'content_type'
        ).prefetch_related('producto')

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def aprobar(self, request, pk=None):
        """Aprueba un movimiento pendiente."""
        movimiento = self.get_object()
        if movimiento.status != movimiento.STATUS_PENDIENTE:
            return Response(
                {'error': 'Solo se pueden aprobar movimientos en estado PENDIENTE'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Opcional: Validar que sea ADMIN
        if request.user.role != 'ADMIN':
            return Response(
                {'error': 'Solo un administrador puede aprobar movimientos'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        try:
            movimiento.status = movimiento.STATUS_APROBADO
            movimiento.save() # Esto disparará el update_stock en el modelo
            return Response({'status': 'Movimiento aprobado y stock actualizado'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rechazar(self, request, pk=None):
        """Rechaza un movimiento pendiente."""
        movimiento = self.get_object()
        if movimiento.status != movimiento.STATUS_PENDIENTE:
            return Response(
                {'error': 'Solo se pueden rechazar movimientos en estado PENDIENTE'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.role != 'ADMIN':
            return Response(
                {'error': 'Solo un administrador puede rechazar movimientos'},
                status=status.HTTP_403_FORBIDDEN
            )

        movimiento.status = movimiento.STATUS_RECHAZADO
        movimiento.save()
        return Response({'status': 'Movimiento rechazado'})

# ============================================================================
# VIEWSET DE REPORTES CONSOLIDADO
# ============================================================================

class RefactoredReportesViewSet(viewsets.ViewSet):
    """ViewSet para reportes consolidados del nuevo sistema."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Estadísticas generales para el dashboard."""
        from inventario.models import Pipe, PumpAndMotor, Sucursal, StockPipe, StockPumpAndMotor
        
        stats = {
            'total_tuberias': Pipe.objects.count(),
            'total_equipos': PumpAndMotor.objects.count(),
            'total_sucursales': Sucursal.objects.count(),
            'total_stock_tuberias': StockPipe.objects.aggregate(total=Sum('cantidad'))['total'] or 0,
            'total_stock_equipos': StockPumpAndMotor.objects.aggregate(total=Sum('cantidad'))['total'] or 0,
        }
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def movimientos_recientes(self, request):
        """Movimientos de inventario de los últimos N días."""
        from inventario.models import MovimientoInventario
        from datetime import timedelta
        from django.utils import timezone
        
        dias = int(request.query_params.get('dias', 30))
        fecha_inicio = timezone.now() - timedelta(days=dias)
        
        movimientos = MovimientoInventario.objects.filter(
            fecha_movimiento__gte=fecha_inicio
        ).order_by('-fecha_movimiento')
        
        serializer = MovimientoInventarioSerializer(movimientos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stock_por_sucursal(self, request):
        """Resumen de stock por sucursal."""
        from inventario.models import Sucursal, Acueducto, StockPipe, StockPumpAndMotor
        
        sucursales = Sucursal.objects.all()
        data = []
        
        for suc in sucursales:
            acueductos = Acueducto.objects.filter(sucursal=suc)
            stock_tuberias = StockPipe.objects.filter(acueducto__in=acueductos).aggregate(total=Sum('cantidad'))['total'] or 0
            stock_equipos = StockPumpAndMotor.objects.filter(acueducto__in=acueductos).aggregate(total=Sum('cantidad'))['total'] or 0
            
            data.append({
                'id': suc.id,
                'nombre': suc.nombre,
                'total_acueductos': acueductos.count(),
                'stock_tuberias': stock_tuberias,
                'stock_equipos': stock_equipos,
                'stock_total': stock_tuberias + stock_equipos
            })
            
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def resumen_movimientos(self, request):
        """Resumen cuantitativo de movimientos por tipo."""
        from inventario.models import MovimientoInventario
        from django.db.models import Count, Sum
        from datetime import timedelta
        from django.utils import timezone
        
        dias = int(request.query_params.get('dias', 30))
        fecha_inicio = timezone.now() - timedelta(days=dias)
        
        resumen = MovimientoInventario.objects.filter(
            fecha_movimiento__gte=fecha_inicio
        ).values('tipo_movimiento').annotate(
            total=Count('id'),
            cantidad_total=Sum('cantidad')
        )
        
        return Response(list(resumen))


# ============================================================================
# VIEWSETS DE ALERTAS Y NOTIFICACIONES
# ============================================================================

class AlertaViewSet(viewsets.ModelViewSet):
    """ViewSet para alertas de stock."""
    # serializer_class se define dinámicamente o asumiendo el nombre en inventario.serializers
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        from inventario.serializers import AlertaSerializer
        return AlertaSerializer
    
    def get_queryset(self):
        from inventario.models import Alerta
        return Alerta.objects.all().select_related('acueducto', 'content_type')

class NotificacionViewSet(viewsets.ModelViewSet):
    """ViewSet para notificaciones."""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        from inventario.serializers import NotificacionSerializer
        return NotificacionSerializer
    
    def get_queryset(self):
        from inventario.models import Notificacion
        return Notificacion.objects.all().order_by('-creada_en')

# ============================================================================
# VIEWSETS DE MANTENIMIENTO Y ORDENES
# ============================================================================

class FichaTecnicaMotorViewSet(viewsets.ModelViewSet):
    queryset = FichaTecnicaMotor.objects.all()
    serializer_class = FichaTecnicaMotorSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['equipo', 'estado_actual']

class RegistroMantenimientoViewSet(viewsets.ModelViewSet):
    queryset = RegistroMantenimiento.objects.all()
    serializer_class = RegistroMantenimientoSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['ficha_tecnica', 'tipo_mantenimiento']

class OrdenCompraViewSet(viewsets.ModelViewSet):
    queryset = OrdenCompra.objects.all()
    serializer_class = OrdenCompraSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['solicitante', 'aprobador', 'movimiento']
    search_fields = ['codigo_orden', 'detalles']


