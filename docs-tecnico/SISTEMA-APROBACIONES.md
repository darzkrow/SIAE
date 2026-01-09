# Sistema de Aprobaciones - Fase 4

**Fecha**: 8 de Enero de 2026  
**Status**: 📋 DISEÑO Y ESPECIFICACIÓN

---

## 🎯 Objetivo

Implementar un sistema de workflow de aprobación para movimientos de inventario grandes, permitiendo que supervisores revisen y aprueben/rechacen movimientos críticos.

---

## 📊 Especificación del Sistema

### 1. Modelo de Datos

```python
class AprobacionMovimiento(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de Aprobación'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]
    
    movimiento = models.OneToOneField(MovimientoInventario, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    solicitante = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='aprobaciones_solicitadas')
    aprobador = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='aprobaciones_realizadas')
    razon_rechazo = models.TextField(blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-fecha_solicitud']
```

### 2. Reglas de Aprobación

```
Movimiento ENTRADA:
  - Cantidad > 100 unidades → Requiere aprobación
  - Cantidad > 500 unidades → Requiere aprobación de 2 supervisores

Movimiento SALIDA:
  - Cantidad > 50 unidades → Requiere aprobación
  - Cantidad > 200 unidades → Requiere aprobación de 2 supervisores

Movimiento TRANSFERENCIA:
  - Entre sucursales diferentes → Requiere aprobación
  - Cantidad > 100 unidades → Requiere aprobación

Movimiento AJUSTE:
  - Siempre requiere aprobación
```

### 3. Flujo de Aprobación

```
Usuario crea movimiento
        ↓
¿Requiere aprobación?
        ↓
    SÍ → Crear AprobacionMovimiento (PENDIENTE)
        ↓
    Notificar a supervisores
        ↓
    Supervisor revisa
        ↓
    ¿Aprueba?
        ↓
    SÍ → Procesar movimiento
        ↓
    NO → Rechazar y notificar
```

---

## 🔧 Implementación

### 1. Crear Modelo

```python
# inventario/models.py

class AprobacionMovimiento(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de Aprobación'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]
    
    movimiento = models.OneToOneField(
        MovimientoInventario, 
        on_delete=models.CASCADE,
        related_name='aprobacion'
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='PENDIENTE'
    )
    solicitante = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='aprobaciones_solicitadas'
    )
    aprobador = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='aprobaciones_realizadas'
    )
    razon_rechazo = models.TextField(blank=True)
    comentarios = models.TextField(blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-fecha_solicitud']
        verbose_name = 'Aprobación de Movimiento'
        verbose_name_plural = 'Aprobaciones de Movimientos'
    
    def __str__(self):
        return f"Aprobación {self.movimiento.id} - {self.estado}"
    
    def aprobar(self, usuario):
        """Aprobar movimiento"""
        self.estado = 'APROBADO'
        self.aprobador = usuario
        self.fecha_aprobacion = timezone.now()
        self.save()
        
        # Procesar movimiento
        self.movimiento.procesar()
        
        # Notificar
        self.notificar_aprobacion()
    
    def rechazar(self, usuario, razon):
        """Rechazar movimiento"""
        self.estado = 'RECHAZADO'
        self.aprobador = usuario
        self.razon_rechazo = razon
        self.fecha_aprobacion = timezone.now()
        self.save()
        
        # Notificar
        self.notificar_rechazo()
    
    def notificar_aprobacion(self):
        """Enviar notificación de aprobación"""
        # Implementar envío de email
        pass
    
    def notificar_rechazo(self):
        """Enviar notificación de rechazo"""
        # Implementar envío de email
        pass
```

### 2. Crear Serializer

```python
# inventario/serializers.py

class AprobacionMovimientoSerializer(serializers.ModelSerializer):
    solicitante_nombre = serializers.ReadOnlyField(source='solicitante.username')
    aprobador_nombre = serializers.ReadOnlyField(source='aprobador.username')
    movimiento_detalle = MovimientoInventarioSerializer(source='movimiento', read_only=True)
    
    class Meta:
        model = AprobacionMovimiento
        fields = [
            'id', 'movimiento', 'movimiento_detalle', 'estado',
            'solicitante', 'solicitante_nombre',
            'aprobador', 'aprobador_nombre',
            'razon_rechazo', 'comentarios',
            'fecha_solicitud', 'fecha_aprobacion'
        ]
        read_only_fields = ['id', 'fecha_solicitud', 'fecha_aprobacion']
```

### 3. Crear ViewSet

```python
# inventario/views.py

class AprobacionMovimientoViewSet(viewsets.ModelViewSet):
    queryset = AprobacionMovimiento.objects.all()
    serializer_class = AprobacionMovimientoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['estado', 'solicitante', 'aprobador']
    ordering_fields = ['fecha_solicitud']
    ordering = ['-fecha_solicitud']
    
    def get_queryset(self):
        """Filtrar según rol"""
        user = self.request.user
        if user.role == 'ADMIN':
            return AprobacionMovimiento.objects.all()
        # Supervisores ven solo aprobaciones de su sucursal
        return AprobacionMovimiento.objects.filter(
            movimiento__acueducto_origen__sucursal=user.sucursal
        )
    
    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        """Aprobar movimiento"""
        aprobacion = self.get_object()
        
        # Validar permisos
        if request.user.role != 'ADMIN':
            return Response(
                {'error': 'Solo administradores pueden aprobar'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        aprobacion.aprobar(request.user)
        return Response({'status': 'Movimiento aprobado'})
    
    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        """Rechazar movimiento"""
        aprobacion = self.get_object()
        razon = request.data.get('razon', '')
        
        # Validar permisos
        if request.user.role != 'ADMIN':
            return Response(
                {'error': 'Solo administradores pueden rechazar'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        aprobacion.rechazar(request.user, razon)
        return Response({'status': 'Movimiento rechazado'})
```

### 4. Registrar en URLs

```python
# inventario/urls.py

router.register(r'aprobaciones', views.AprobacionMovimientoViewSet, basename='aprobaciones')
```

---

## 📱 Frontend

### Componente de Aprobaciones

```jsx
// frontend/src/pages/Aprobaciones.jsx

import { useState, useEffect } from 'react';
import axios from 'axios';
import Swal from 'sweetalert2';

export default function Aprobaciones() {
    const [aprobaciones, setAprobaciones] = useState([]);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        fetchAprobaciones();
    }, []);
    
    const fetchAprobaciones = async () => {
        try {
            const res = await axios.get('/api/aprobaciones/?estado=PENDIENTE');
            setAprobaciones(res.data.results || res.data);
        } catch (err) {
            console.error('Error:', err);
        } finally {
            setLoading(false);
        }
    };
    
    const handleAprobar = async (id) => {
        try {
            await axios.post(`/api/aprobaciones/${id}/aprobar/`);
            Swal.fire({
                icon: 'success',
                title: 'Aprobado',
                text: 'Movimiento aprobado exitosamente'
            });
            fetchAprobaciones();
        } catch (err) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'No se pudo aprobar el movimiento'
            });
        }
    };
    
    const handleRechazar = async (id) => {
        const { value: razon } = await Swal.fire({
            title: 'Rechazar Movimiento',
            input: 'textarea',
            inputLabel: 'Razón del rechazo',
            inputPlaceholder: 'Ingresa la razón...',
            showCancelButton: true
        });
        
        if (razon) {
            try {
                await axios.post(`/api/aprobaciones/${id}/rechazar/`, { razon });
                Swal.fire({
                    icon: 'success',
                    title: 'Rechazado',
                    text: 'Movimiento rechazado'
                });
                fetchAprobaciones();
            } catch (err) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'No se pudo rechazar el movimiento'
                });
            }
        }
    };
    
    if (loading) return <div>Cargando...</div>;
    
    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold">Aprobaciones Pendientes</h1>
            
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="w-full">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left">Movimiento</th>
                            <th className="px-6 py-3 text-left">Tipo</th>
                            <th className="px-6 py-3 text-left">Cantidad</th>
                            <th className="px-6 py-3 text-left">Solicitante</th>
                            <th className="px-6 py-3 text-left">Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {aprobaciones.map(aprobacion => (
                            <tr key={aprobacion.id} className="border-t">
                                <td className="px-6 py-4">{aprobacion.movimiento}</td>
                                <td className="px-6 py-4">{aprobacion.movimiento_detalle.tipo_movimiento}</td>
                                <td className="px-6 py-4">{aprobacion.movimiento_detalle.cantidad}</td>
                                <td className="px-6 py-4">{aprobacion.solicitante_nombre}</td>
                                <td className="px-6 py-4 space-x-2">
                                    <button
                                        onClick={() => handleAprobar(aprobacion.id)}
                                        className="px-3 py-1 bg-green-600 text-white rounded"
                                    >
                                        Aprobar
                                    </button>
                                    <button
                                        onClick={() => handleRechazar(aprobacion.id)}
                                        className="px-3 py-1 bg-red-600 text-white rounded"
                                    >
                                        Rechazar
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
```

---

## 📧 Notificaciones

### Email de Aprobación

```
Asunto: Movimiento Aprobado - ID: 123

Hola [Solicitante],

Tu movimiento ha sido aprobado:
- Tipo: ENTRADA
- Cantidad: 50 unidades
- Artículo: Tubería PVC 2 pulgadas
- Aprobador: [Nombre del Aprobador]

El movimiento ha sido procesado exitosamente.

Saludos,
GSIH Inventario
```

### Email de Rechazo

```
Asunto: Movimiento Rechazado - ID: 123

Hola [Solicitante],

Tu movimiento ha sido rechazado:
- Tipo: ENTRADA
- Cantidad: 50 unidades
- Artículo: Tubería PVC 2 pulgadas
- Razón: [Razón del rechazo]

Por favor, contacta al aprobador para más información.

Saludos,
GSIH Inventario
```

---

## 🧪 Pruebas

### Test de Aprobación

```python
def test_aprobar_movimiento():
    aprobacion = AprobacionMovimiento.objects.create(
        movimiento=movimiento,
        solicitante=usuario1,
        estado='PENDIENTE'
    )
    
    aprobacion.aprobar(usuario_admin)
    
    assert aprobacion.estado == 'APROBADO'
    assert aprobacion.aprobador == usuario_admin
    assert aprobacion.fecha_aprobacion is not None
```

---

## 📊 Reportes

### Reporte de Aprobaciones

```
GET /api/reportes/aprobaciones/?periodo=mes

Response:
{
  "total_solicitudes": 50,
  "aprobadas": 45,
  "rechazadas": 3,
  "pendientes": 2,
  "tasa_aprobacion": 93.75,
  "tiempo_promedio_aprobacion": "2 horas"
}
```

---

## 🎯 Próximos Pasos

1. Implementar modelo y serializer
2. Crear viewset con acciones
3. Desarrollar componente frontend
4. Implementar notificaciones por email
5. Agregar reportes
6. Pruebas completas

---

**Status**: 📋 ESPECIFICACIÓN COMPLETA - LISTO PARA IMPLEMENTAR
