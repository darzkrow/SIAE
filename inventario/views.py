from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .permissions import IsAdminOrReadOnly, IsAdminOrSameSucursal, CanManageUsers
from accounts.models import CustomUser
from .models import (
    OrganizacionCentral, Sucursal, Acueducto, 
    Categoria, Tuberia, Equipo, StockTuberia, StockEquipo, 
    MovimientoInventario, InventoryAudit, AlertaStock, Notification
)
from .serializers import (
    OrganizacionCentralSerializer, SucursalSerializer, 
    AcueductoSerializer, CategoriaSerializer, TuberiaSerializer, 
    EquipoSerializer, StockTuberiaSerializer, StockEquipoSerializer, 
    MovimientoInventarioSerializer, InventoryAuditSerializer, AlertaStockSerializer, NotificationSerializer
)

class OrganizacionCentralViewSet(viewsets.ModelViewSet):
    queryset = OrganizacionCentral.objects.all()
    serializer_class = OrganizacionCentralSerializer
    permission_classes = [IsAdminOrReadOnly]

class SucursalViewSet(viewsets.ModelViewSet):
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        """Filtrar sucursales según el rol del usuario"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Administradores ven todas las sucursales
        if user.role == user.ROLE_ADMIN:
            return queryset
        
        # Operadores solo ven su sucursal
        if user.sucursal:
            return queryset.filter(id=user.sucursal.id)
        
        return queryset.none()

class AcueductoViewSet(viewsets.ModelViewSet):
    queryset = Acueducto.objects.all()
    serializer_class = AcueductoSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        """Filtrar acueductos según el rol del usuario"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Administradores ven todos los acueductos
        if user.role == user.ROLE_ADMIN:
            return queryset
        
        # Operadores solo ven acueductos de su sucursal
        if user.sucursal:
            return queryset.filter(sucursal=user.sucursal)
        
        return queryset.none()

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAdminOrReadOnly]

class TuberiaViewSet(viewsets.ModelViewSet):
    queryset = Tuberia.objects.all()
    serializer_class = TuberiaSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['material', 'tipo_uso', 'categoria']
    search_fields = ['nombre', 'descripcion']

class EquipoViewSet(viewsets.ModelViewSet):
    queryset = Equipo.objects.all()
    serializer_class = EquipoSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['marca', 'categoria']
    search_fields = ['nombre', 'descripcion', 'marca', 'modelo', 'numero_serie']

class StockTuberiaViewSet(viewsets.ModelViewSet):
    queryset = StockTuberia.objects.all()
    serializer_class = StockTuberiaSerializer
    permission_classes = [IsAdminOrSameSucursal]
    
    def get_queryset(self):
        """Filtrar stock según el rol del usuario"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Administradores ven todo el stock
        if user.role == user.ROLE_ADMIN:
            return queryset
        
        # Operadores solo ven stock de su sucursal
        if user.sucursal:
            return queryset.filter(acueducto__sucursal=user.sucursal)
        
        return queryset.none()

class StockEquipoViewSet(viewsets.ModelViewSet):
    queryset = StockEquipo.objects.all()
    serializer_class = StockEquipoSerializer
    permission_classes = [IsAdminOrSameSucursal]
    
    def get_queryset(self):
        """Filtrar stock según el rol del usuario"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Administradores ven todo el stock
        if user.role == user.ROLE_ADMIN:
            return queryset
        
        # Operadores solo ven stock de su sucursal
        if user.sucursal:
            return queryset.filter(acueducto__sucursal=user.sucursal)
        
        return queryset.none()

class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    queryset = MovimientoInventario.objects.all().order_by('-fecha_movimiento')
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [IsAdminOrSameSucursal]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tipo_movimiento', 'acueducto_origen', 'acueducto_destino']
    ordering_fields = ['fecha_movimiento']
    ordering = ['-fecha_movimiento']
    
    def get_queryset(self):
        """Filtrar movimientos según el rol del usuario"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Administradores ven todos los movimientos
        if user.role == user.ROLE_ADMIN:
            return queryset
        
        # Operadores solo ven movimientos de su sucursal
        if user.sucursal:
            return queryset.filter(
                Q(acueducto_origen__sucursal=user.sucursal) |
                Q(acueducto_destino__sucursal=user.sucursal)
            )
        
        return queryset.none()

class InventoryAuditViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryAudit.objects.all().order_by('-fecha')
    serializer_class = InventoryAuditSerializer
    permission_classes = [IsAdminOrSameSucursal]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'tipo_movimiento', 'articulo_tipo']
    ordering_fields = ['fecha']
    ordering = ['-fecha']
    
    def get_queryset(self):
        """Filtrar auditorías según el rol del usuario"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Administradores ven todas las auditorías
        if user.role == user.ROLE_ADMIN:
            return queryset
        
        # Operadores solo ven auditorías de su sucursal
        if user.sucursal:
            return queryset.filter(
                Q(acueducto_origen__sucursal=user.sucursal) |
                Q(acueducto_destino__sucursal=user.sucursal)
            )
        
        return queryset.none()

class AlertaStockViewSet(viewsets.ModelViewSet):
    queryset = AlertaStock.objects.all()
    serializer_class = AlertaStockSerializer
    permission_classes = [permissions.IsAuthenticated]

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

class ReportesViewSet(viewsets.ViewSet):
    """
    ViewSet para generar reportes y estadísticas del inventario
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Estadísticas para el dashboard principal"""
        stats = {
            'total_tuberias': Tuberia.objects.count(),
            'total_equipos': Equipo.objects.count(),
            'total_sucursales': Sucursal.objects.count(),
            'total_acueductos': Acueducto.objects.count(),
            'total_stock_tuberias': StockTuberia.objects.aggregate(total=Sum('cantidad'))['total'] or 0,
            'total_stock_equipos': StockEquipo.objects.aggregate(total=Sum('cantidad'))['total'] or 0,
            'alertas_activas': AlertaStock.objects.filter(activo=True).count(),
            'movimientos_hoy': MovimientoInventario.objects.filter(
                fecha_movimiento__date=timezone.now().date()
            ).count(),
        }
        return Response(stats)

    @action(detail=False, methods=['get'])
    def stock_por_sucursal(self, request):
        """Stock agrupado por sucursal"""
        sucursales_data = []
        
        for sucursal in Sucursal.objects.all():
            acueductos = sucursal.acueductos.all()
            
            stock_tuberias = StockTuberia.objects.filter(
                acueducto__in=acueductos
            ).aggregate(total=Sum('cantidad'))['total'] or 0
            
            stock_equipos = StockEquipo.objects.filter(
                acueducto__in=acueductos
            ).aggregate(total=Sum('cantidad'))['total'] or 0
            
            sucursales_data.append({
                'id': sucursal.id,
                'nombre': sucursal.nombre,
                'total_acueductos': acueductos.count(),
                'stock_tuberias': stock_tuberias,
                'stock_equipos': stock_equipos,
                'stock_total': stock_tuberias + stock_equipos
            })
        
        return Response(sucursales_data)

    @action(detail=False, methods=['get'])
    def movimientos_recientes(self, request):
        """Últimos movimientos de inventario"""
        dias = int(request.query_params.get('dias', 7))
        fecha_desde = timezone.now() - timedelta(days=dias)
        
        movimientos = MovimientoInventario.objects.filter(
            fecha_movimiento__gte=fecha_desde
        ).order_by('-fecha_movimiento')[:20]
        
        serializer = MovimientoInventarioSerializer(movimientos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def alertas_stock_bajo(self, request):
        """Artículos con stock por debajo del umbral"""
        alertas_criticas = []
        
        for alerta in AlertaStock.objects.filter(activo=True):
            if alerta.tuberia:
                try:
                    stock = StockTuberia.objects.get(
                        tuberia=alerta.tuberia, 
                        acueducto=alerta.acueducto
                    )
                    cantidad_actual = stock.cantidad
                except StockTuberia.DoesNotExist:
                    cantidad_actual = 0
                
                if cantidad_actual <= alerta.umbral_minimo:
                    alertas_criticas.append({
                        'tipo': 'tuberia',
                        'articulo': str(alerta.tuberia),
                        'acueducto': str(alerta.acueducto),
                        'cantidad_actual': cantidad_actual,
                        'umbral_minimo': alerta.umbral_minimo,
                        'diferencia': alerta.umbral_minimo - cantidad_actual
                    })
            
            elif alerta.equipo:
                try:
                    stock = StockEquipo.objects.get(
                        equipo=alerta.equipo, 
                        acueducto=alerta.acueducto
                    )
                    cantidad_actual = stock.cantidad
                except StockEquipo.DoesNotExist:
                    cantidad_actual = 0
                
                if cantidad_actual <= alerta.umbral_minimo:
                    alertas_criticas.append({
                        'tipo': 'equipo',
                        'articulo': str(alerta.equipo),
                        'acueducto': str(alerta.acueducto),
                        'cantidad_actual': cantidad_actual,
                        'umbral_minimo': alerta.umbral_minimo,
                        'diferencia': alerta.umbral_minimo - cantidad_actual
                    })
        
        return Response(alertas_criticas)

    @action(detail=False, methods=['get'])
    def resumen_movimientos(self, request):
        """Resumen de movimientos por tipo en un período"""
        dias = int(request.query_params.get('dias', 30))
        fecha_desde = timezone.now() - timedelta(days=dias)
        
        resumen = MovimientoInventario.objects.filter(
            fecha_movimiento__gte=fecha_desde
        ).values('tipo_movimiento').annotate(
            total=Count('id'),
            cantidad_total=Sum('cantidad')
        ).order_by('tipo_movimiento')
        
        return Response(list(resumen))

    @action(detail=False, methods=['get'])
    def stock_search(self, request):
        """Búsqueda de stock de artículo específico por ubicación con validaciones"""
        articulo_id = request.query_params.get('articulo_id')
        articulo_tipo = request.query_params.get('tipo')  # 'tuberia' o 'equipo'
        sucursal_id = request.query_params.get('sucursal_id')
        
        # Validación 1: Parámetros requeridos
        if not articulo_id or not articulo_tipo:
            return Response(
                {'error': 'Se requieren parámetros: articulo_id y tipo'},
                status=400
            )
        
        # Validación 2: Tipo de artículo válido
        if articulo_tipo not in ['tuberia', 'equipo']:
            return Response(
                {'error': 'Tipo de artículo inválido. Debe ser "tuberia" o "equipo"'},
                status=400
            )
        
        # Validación 3: ID debe ser numérico
        try:
            articulo_id = int(articulo_id)
        except (ValueError, TypeError):
            return Response(
                {'error': 'articulo_id debe ser un número válido'},
                status=400
            )
        
        # Validación 4: sucursal_id debe ser numérico si se proporciona
        if sucursal_id:
            try:
                sucursal_id = int(sucursal_id)
                # Verificar que la sucursal existe
                if not Sucursal.objects.filter(id=sucursal_id).exists():
                    return Response(
                        {'error': f'Sucursal con ID {sucursal_id} no encontrada'},
                        status=404
                    )
            except (ValueError, TypeError):
                return Response(
                    {'error': 'sucursal_id debe ser un número válido'},
                    status=400
                )
        
        resultados = []
        articulo_obj = None
        
        if articulo_tipo == 'tuberia':
            try:
                articulo_obj = Tuberia.objects.get(id=articulo_id)
                stocks = StockTuberia.objects.filter(tuberia=articulo_obj)
                
                if sucursal_id:
                    stocks = stocks.filter(acueducto__sucursal_id=sucursal_id)
                
                # Validación 5: Verificar que hay stock disponible
                if not stocks.exists():
                    return Response({
                        'articulo_id': articulo_id,
                        'tipo': articulo_tipo,
                        'total_ubicaciones': 0,
                        'stock_total': 0,
                        'mensaje': 'No hay stock disponible para este artículo',
                        'resultados': []
                    })
                
                for stock in stocks:
                    resultados.append({
                        'id': stock.id,
                        'articulo': str(articulo_obj),
                        'articulo_id': articulo_obj.id,
                        'tipo': 'tuberia',
                        'acueducto': str(stock.acueducto),
                        'acueducto_id': stock.acueducto.id,
                        'sucursal': str(stock.acueducto.sucursal),
                        'sucursal_id': stock.acueducto.sucursal.id,
                        'cantidad': stock.cantidad,
                        'fecha_actualizacion': stock.fecha_ultima_actualizacion,
                        'estado': 'bajo' if stock.cantidad <= 10 else 'normal'
                    })
            except Tuberia.DoesNotExist:
                return Response(
                    {'error': f'Tubería con ID {articulo_id} no encontrada'},
                    status=404
                )
        
        elif articulo_tipo == 'equipo':
            try:
                articulo_obj = Equipo.objects.get(id=articulo_id)
                stocks = StockEquipo.objects.filter(equipo=articulo_obj)
                
                if sucursal_id:
                    stocks = stocks.filter(acueducto__sucursal_id=sucursal_id)
                
                # Validación 5: Verificar que hay stock disponible
                if not stocks.exists():
                    return Response({
                        'articulo_id': articulo_id,
                        'tipo': articulo_tipo,
                        'total_ubicaciones': 0,
                        'stock_total': 0,
                        'mensaje': 'No hay stock disponible para este artículo',
                        'resultados': []
                    })
                
                for stock in stocks:
                    resultados.append({
                        'id': stock.id,
                        'articulo': str(articulo_obj),
                        'articulo_id': articulo_obj.id,
                        'tipo': 'equipo',
                        'acueducto': str(stock.acueducto),
                        'acueducto_id': stock.acueducto.id,
                        'sucursal': str(stock.acueducto.sucursal),
                        'sucursal_id': stock.acueducto.sucursal.id,
                        'cantidad': stock.cantidad,
                        'fecha_actualizacion': stock.fecha_ultima_actualizacion,
                        'estado': 'bajo' if stock.cantidad <= 10 else 'normal'
                    })
            except Equipo.DoesNotExist:
                return Response(
                    {'error': f'Equipo con ID {articulo_id} no encontrada'},
                    status=404
                )
        
        stock_total = sum(r['cantidad'] for r in resultados) if resultados else 0
        
        return Response({
            'articulo_id': articulo_id,
            'articulo': str(articulo_obj) if articulo_obj else None,
            'tipo': articulo_tipo,
            'total_ubicaciones': len(resultados),
            'stock_total': stock_total,
            'sucursal_filtrada': sucursal_id,
            'resultados': resultados
        })

    @action(detail=False, methods=['get'])
    def stock_search_advanced(self, request):
        """Búsqueda avanzada de stock con múltiples filtros"""
        # Parámetros de búsqueda
        nombre_articulo = request.query_params.get('nombre', '').strip()
        sucursal_id = request.query_params.get('sucursal_id')
        acueducto_id = request.query_params.get('acueducto_id')
        articulo_tipo = request.query_params.get('tipo')  # 'tuberia', 'equipo' o 'all'
        stock_bajo = request.query_params.get('stock_bajo', 'false').lower() == 'true'
        
        # Validación: Al menos un parámetro de búsqueda
        if not nombre_articulo and not sucursal_id and not acueducto_id:
            return Response(
                {'error': 'Se requiere al menos uno de: nombre, sucursal_id o acueducto_id'},
                status=400
            )
        
        resultados = []
        
        # Búsqueda en Tuberías
        if articulo_tipo in ['tuberia', 'all']:
            stocks_tuberia = StockTuberia.objects.all()
            
            if nombre_articulo:
                stocks_tuberia = stocks_tuberia.filter(
                    Q(tuberia__nombre__icontains=nombre_articulo) |
                    Q(tuberia__descripcion__icontains=nombre_articulo)
                )
            
            if sucursal_id:
                try:
                    sucursal_id = int(sucursal_id)
                    stocks_tuberia = stocks_tuberia.filter(acueducto__sucursal_id=sucursal_id)
                except (ValueError, TypeError):
                    return Response({'error': 'sucursal_id debe ser numérico'}, status=400)
            
            if acueducto_id:
                try:
                    acueducto_id = int(acueducto_id)
                    stocks_tuberia = stocks_tuberia.filter(acueducto_id=acueducto_id)
                except (ValueError, TypeError):
                    return Response({'error': 'acueducto_id debe ser numérico'}, status=400)
            
            if stock_bajo:
                stocks_tuberia = stocks_tuberia.filter(cantidad__lte=10)
            
            for stock in stocks_tuberia:
                resultados.append({
                    'id': stock.id,
                    'articulo': str(stock.tuberia),
                    'articulo_id': stock.tuberia.id,
                    'tipo': 'tuberia',
                    'acueducto': str(stock.acueducto),
                    'acueducto_id': stock.acueducto.id,
                    'sucursal': str(stock.acueducto.sucursal),
                    'sucursal_id': stock.acueducto.sucursal.id,
                    'cantidad': stock.cantidad,
                    'fecha_actualizacion': stock.fecha_ultima_actualizacion,
                    'estado': 'bajo' if stock.cantidad <= 10 else 'normal'
                })
        
        # Búsqueda en Equipos
        if articulo_tipo in ['equipo', 'all']:
            stocks_equipo = StockEquipo.objects.all()
            
            if nombre_articulo:
                stocks_equipo = stocks_equipo.filter(
                    Q(equipo__nombre__icontains=nombre_articulo) |
                    Q(equipo__descripcion__icontains=nombre_articulo)
                )
            
            if sucursal_id:
                try:
                    sucursal_id = int(sucursal_id)
                    stocks_equipo = stocks_equipo.filter(acueducto__sucursal_id=sucursal_id)
                except (ValueError, TypeError):
                    return Response({'error': 'sucursal_id debe ser numérico'}, status=400)
            
            if acueducto_id:
                try:
                    acueducto_id = int(acueducto_id)
                    stocks_equipo = stocks_equipo.filter(acueducto_id=acueducto_id)
                except (ValueError, TypeError):
                    return Response({'error': 'acueducto_id debe ser numérico'}, status=400)
            
            if stock_bajo:
                stocks_equipo = stocks_equipo.filter(cantidad__lte=10)
            
            for stock in stocks_equipo:
                resultados.append({
                    'id': stock.id,
                    'articulo': str(stock.equipo),
                    'articulo_id': stock.equipo.id,
                    'tipo': 'equipo',
                    'acueducto': str(stock.acueducto),
                    'acueducto_id': stock.acueducto.id,
                    'sucursal': str(stock.acueducto.sucursal),
                    'sucursal_id': stock.acueducto.sucursal.id,
                    'cantidad': stock.cantidad,
                    'fecha_actualizacion': stock.fecha_ultima_actualizacion,
                    'estado': 'bajo' if stock.cantidad <= 10 else 'normal'
                })
        
        # Ordenar por cantidad (menor primero si stock_bajo está activo)
        if stock_bajo:
            resultados.sort(key=lambda x: x['cantidad'])
        
        return Response({
            'filtros': {
                'nombre': nombre_articulo,
                'sucursal_id': sucursal_id,
                'acueducto_id': acueducto_id,
                'tipo': articulo_tipo,
                'stock_bajo': stock_bajo
            },
            'total_resultados': len(resultados),
            'stock_total': sum(r['cantidad'] for r in resultados),
            'resultados': resultados
        })


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = None  # Will be set dynamically
    permission_classes = [CanManageUsers]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    def get_serializer_class(self):
        from .serializers import CustomUserSerializer
        return CustomUserSerializer
    
    def get_queryset(self):
        """Solo ADMIN puede ver todos los usuarios"""
        user = self.request.user
        if user.role == 'ADMIN':
            return CustomUser.objects.all()
        return CustomUser.objects.none()
