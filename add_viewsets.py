"""
Script para agregar SubalmacenViewSet y endpoints de aprobación QR
"""

# Leer el archivo views.py
with open(r'c:\Users\gfranco\Desktop\SIAE\backend\institucion\views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Agregar import de Subalmacen y SubalmacenSerializer
if "Subalmacen" not in content:
    content = content.replace(
        "from .models import (",
        "from .models import (\n    Subalmacen,"
    )

if "SubalmacenSerializer" not in content:
    content = content.replace(
        "from .serializers import (",
        "from .serializers import (\n    SubalmacenSerializer,"
    )

# 2. ViewSet de Subalmacén
subalmacen_viewset = '''

class SubalmacenViewSet(BaseModelViewSet):
    """
    ViewSet para gestión de Subalmacenes con ubicación geográfica.
    """
    queryset = Subalmacen.objects.all()
    serializer_class = SubalmacenSerializer
    filterset_fields = ['estado', 'municipio', 'parroquia', 'sucursal', 'activo']
    search_fields = ['nombre', 'codigo', 'direccion']
    ordering_fields = ['nombre', 'codigo', 'estado__name', 'created_at']
    
    def get_queryset(self):
        """Optimize queryset with select_related"""
        return super().get_queryset().select_related(
            'sucursal',
            'estado',
            'municipio',
            'parroquia',
            'responsable'
        )
    
    @action(detail=False, methods=['get'], url_path='por-estado/(?P<estado_id>[^/.]+)')
    def por_estado(self, request, estado_id=None):
        """Listar subalmacenes por estado"""
        subalmacenes = self.get_queryset().filter(
            estado_id=estado_id,
            activo=True
        )
        serializer = self.get_serializer(subalmacenes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='por-sucursal/(?P<sucursal_id>[^/.]+)')
    def por_sucursal(self, request, sucursal_id=None):
        """Listar subalmacenes por sucursal"""
        subalmacenes = self.get_queryset().filter(
            sucursal_id=sucursal_id,
            activo=True
        )
        serializer = self.get_serializer(subalmacenes, many=True)
        return Response(serializer.data)

'''

# 3. Endpoints de aprobación con QR para SolicitudTrasladoViewSet
approval_actions = '''
    
    @action(detail=True, methods=['post'], url_path='aprobar-origen')
    def aprobar_origen(self, request, pk=None):
        """
        Aprobar solicitud desde almacén de origen.
        Puede ser llamado escaneando el QR code.
        """
        solicitud = self.get_object()
        
        # Validar que el usuario es responsable del almacén origen
        if not solicitud.almacen_origen.manager or solicitud.almacen_origen.manager != request.user:
            if not request.user.is_staff:
                return Response(
                    {'error': 'No tiene permisos para aprobar desde este almacén'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Validar estado
        if solicitud.estado != 'PENDIENTE':
            return Response(
                {'error': f'Solicitud en estado {solicitud.estado}, no se puede aprobar'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear aprobación
        from .models import AprobacionTraslado
        aprobacion = AprobacionTraslado.objects.create(
            solicitud=solicitud,
            tipo_aprobacion='ORIGEN',
            aprobador=request.user,
            decision='APROBADO',
            comentarios=request.data.get('comentarios', '')
        )
        
        # Actualizar solicitud
        solicitud.aprobacion_origen = aprobacion
        solicitud.estado = 'APROBADA_ORIGEN'
        solicitud.save()
        
        return Response({
            'message': 'Solicitud aprobada por origen',
            'estado': solicitud.estado,
            'siguiente_paso': 'Esperando aprobación de destino'
        })
    
    @action(detail=True, methods=['post'], url_path='aprobar-destino')
    def aprobar_destino(self, request, pk=None):
        """
        Aprobar solicitud desde almacén de destino.
        Puede ser llamado escaneando el QR code.
        """
        solicitud = self.get_object()
        
        # Validar que el usuario es responsable del almacén destino
        if not solicitud.almacen_destino.manager or solicitud.almacen_destino.manager != request.user:
            if not request.user.is_staff:
                return Response(
                    {'error': 'No tiene permisos para aprobar desde este almacén'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Validar estado
        if solicitud.estado != 'APROBADA_ORIGEN':
            return Response(
                {'error': 'Solicitud debe estar aprobada por origen primero'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear aprobación
        from .models import AprobacionTraslado
        aprobacion = AprobacionTraslado.objects.create(
            solicitud=solicitud,
            tipo_aprobacion='DESTINO',
            aprobador=request.user,
            decision='APROBADO',
            comentarios=request.data.get('comentarios', '')
        )
        
        # Actualizar solicitud
        solicitud.aprobacion_destino = aprobacion
        solicitud.estado = 'APROBADA_COMPLETA'
        solicitud.save()
        
        # Ejecutar traslado automáticamente
        try:
            solicitud.ejecutar_traslado(request.user)
        except Exception as e:
            return Response(
                {'error': f'Error al ejecutar traslado: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'message': 'Solicitud completamente aprobada y ejecutada',
            'estado': solicitud.estado,
        })
    
    @action(detail=True, methods=['post'], url_path='rechazar')
    def rechazar(self, request, pk=None):
        """Rechazar solicitud de traslado"""
        solicitud = self.get_object()
        
        # Validar permisos
        if not request.user.is_staff:
            if solicitud.almacen_origen.manager != request.user and solicitud.almacen_destino.manager != request.user:
                return Response(
                    {'error': 'No tiene permisos para rechazar esta solicitud'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Validar estado
        if solicitud.estado not in ['PENDIENTE', 'APROBADA_ORIGEN']:
            return Response(
                {'error': f'No se puede rechazar solicitud en estado {solicitud.estado}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar estado
        solicitud.estado = 'RECHAZADA'
        solicitud.observaciones += f"\\n[{timezone.now()}] Rechazada por {request.user.username}: {request.data.get('motivo', 'Sin motivo')}"
        solicitud.save()
        
        return Response({
            'message': 'Solicitud rechazada',
            'estado': solicitud.estado,
        })
    
    @action(detail=True, methods=['get'], url_path='qr-code')
    def obtener_qr(self, request, pk=None):
        """Obtener o regenerar el QR code de la solicitud"""
        solicitud = self.get_object()
        
        if not solicitud.qr_code:
            solicitud.generar_qr_code(request)
        
        return Response({
            'qr_url': request.build_absolute_uri(solicitud.qr_code.url) if solicitud.qr_code else None,
            'approval_url': solicitud.qr_url,
            'numero_solicitud': solicitud.numero_solicitud,
            'estado': solicitud.estado,
        })
'''

# Insertar SubalmacenViewSet antes de la sección LEGACY
if "class SubalmacenViewSet" not in content:
    content = content.replace(
        "# ============================================================================\n# LEGACY VIEWSETS",
        subalmacen_viewset + "\n# ============================================================================\n# LEGACY VIEWSETS"
    )

# Buscar SolicitudTrasladoViewSet y agregar los métodos de aprobación
if "@action(detail=True, methods=['post'], url_path='aprobar-origen')" not in content:
    # Buscar el final de la clase SolicitudTrasladoViewSet
    import re
    pattern = r"(class SolicitudTrasladoViewSet.*?)(class \w+ViewSet|# ===)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        # Insertar antes de la siguiente clase o sección
        insert_pos = match.end(1)
        content = content[:insert_pos] + approval_actions + "\n\n" + content[insert_pos:]

# Guardar el archivo modificado
with open(r'c:\Users\gfranco\Desktop\SIAE\backend\institucion\views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ SubalmacenViewSet agregado")
print("✅ Endpoints de aprobación con QR agregados a SolicitudTrasladoViewSet")
print("✅ Imports actualizados")
