"""
Views refactorizadas para el sistema de inventario.
ViewSets optimizados con filtros, búsqueda y paginación.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, F, Count
from decimal import Decimal

# Importar permisos existentes
from inventario.permissions import IsAdminOrReadOnly, IsAdminOrSameSucursal

# Imports de modelos y serializers
from inventario.models import (
    Category, UnitOfMeasure, Supplier,
    ChemicalProduct, Pipe, PumpAndMotor, Accessory,
    StockChemical, StockPipe, StockPumpAndMotor, StockAccessory
)
from inventario.serializers import (
    CategorySerializer, UnitOfMeasureSerializer, SupplierSerializer,
    ChemicalProductSerializer, PipeSerializer,
    PumpAndMotorSerializer, AccessorySerializer,
    StockChemicalSerializer, StockPipeSerializer,
    StockPumpAndMotorSerializer, StockAccessorySerializer,
    ChemicalProductListSerializer, PipeListSerializer,
    PumpAndMotorListSerializer, AccessoryListSerializer,
    MovimientoInventarioSerializer
)


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
    from inventario.models import Acueducto
    queryset = Acueducto.objects.all()
    
    def get_serializer_class(self):
        from inventario.serializers import AcueductoSerializer
        return AcueductoSerializer
        
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sucursal', 'activo']
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
    search_fields = ['razon', 'producto__sku']  # Note: producto__sku might not work with GenericFK directly in basic SearchFilter without more config, keeping it simple
    ordering = ['-fecha_movimiento']

    def get_queryset(self):
        from inventario.models import MovimientoInventario
        return MovimientoInventario.objects.all().select_related(
            'acueducto_origen', 'acueducto_destino', 'creado_por', 'content_type'
        )

# ============================================================================
# VIEWSET DE REPORTES CONSOLIDADO
# ============================================================================

class RefactoredReportesViewSet(viewsets.ViewSet):
    """ViewSet para reportes consolidados del nuevo sistema."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Estadísticas generales para el dashboard."""
        # TODO: Implementar después de la migración
        stats = {
            'total_productos': 0,
            'total_quimicos': 0,
            'total_tuberias': 0,
            'total_bombas': 0,
            'total_accesorios': 0,
            'productos_criticos': 0,
            'quimicos_peligrosos': 0,
            'quimicos_proximos_vencer': 0,
            'valor_total_inventario': 0
        }
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def stock_por_categoria(self, request):
        """Stock agrupado por categoría."""
        # TODO: Implementar
        return Response([])
    
    @action(detail=False, methods=['get'])
    def valor_inventario_por_tipo(self, request):
        """Valor del inventario por tipo de producto."""
        # TODO: Implementar
        return Response([])


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
        return Notificacion.objects.all()
