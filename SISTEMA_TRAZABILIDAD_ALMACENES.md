# 🏭 Sistema de Trazabilidad de Almacenes Regionales - Hidroven

## 🎯 Requerimientos del Sistema

### **Nueva Estructura Organizacional con Almacenes**
```
HIDROVEN
├── VP Comercialización
├── VP Operaciones Hídricas
│   ├── Almacén Regional 1 (Estado Zulia) - Prefijo: ZUL
│   ├── Almacén Regional 2 (Estado Carabobo) - Prefijo: CAR
│   ├── Almacén Regional 3 (Estado Miranda) - Prefijo: MIR
│   ├── Almacén Regional 4 (Estado Aragua) - Prefijo: ARA
│   ├── Almacén Regional 5 (Estado Lara) - Prefijo: LAR
│   ├── Almacén Regional 6 (Estado Táchira) - Prefijo: TAC
│   ├── Almacén Regional 7 (Estado Bolívar) - Prefijo: BOL
│   ├── Almacén Regional 8 (Estado Anzoátegui) - Prefijo: ANZ
│   └── Almacén Regional 9 (Estado Monagas) - Prefijo: MON
└── VP Administrativa
```

### **Lógica de Negocio - Trazabilidad de Activos**

#### **1. Código Único de Activo**
- **Formato**: `{PREFIJO_ALMACEN_ORIGEN}-{TIPO_PRODUCTO}-{NUMERO_SECUENCIAL}-{AÑO}`
- **Ejemplo**: `ZUL-BOMBA-000001-2024`
- **Evolución**: `ZUL-BOMBA-000001-2024 → CAR-ZUL-BOMBA-000001-2024`

#### **2. Historial de Vida del Activo**
- **Ubicación Actual**: Dónde se encuentra físicamente
- **Historial de Movimientos**: Todos los traslados realizados
- **Estado del Activo**: EN_ALMACEN, EN_TRANSITO, INSTALADO, EN_USO, MANTENIMIENTO
- **Responsables**: Quién aprobó, quién trasladó, quién recibió
- **Trazabilidad Completa**: Desde origen hasta destino final

#### **3. Flujo de Aprobación**
```
Solicitud de Traslado
    ↓
Aprobación Responsable Almacén Origen
    ↓
Aprobación Responsable Almacén Destino
    ↓
Ejecución del Traslado
    ↓
Confirmación de Recepción
    ↓
Actualización de Inventario
```

---

## 🏗️ **Modelos de Datos Actualizados**

### **Modelo: AlmacenRegional**
```python
class AlmacenRegional(SoftDeleteModel):
    """Almacenes regionales bajo VP de Operaciones"""
    
    class EstadoVenezuela(models.TextChoices):
        ZULIA = 'ZULIA', 'Zulia'
        CARABOBO = 'CARABOBO', 'Carabobo'
        MIRANDA = 'MIRANDA', 'Miranda'
        ARAGUA = 'ARAGUA', 'Aragua'
        LARA = 'LARA', 'Lara'
        TACHIRA = 'TACHIRA', 'Táchira'
        BOLIVAR = 'BOLIVAR', 'Bolívar'
        ANZOATEGUI = 'ANZOATEGUI', 'Anzoátegui'
        MONAGAS = 'MONAGAS', 'Monagas'
    
    vicepresidencia_operaciones = models.ForeignKey(
        'Vicepresidencia',
        on_delete=models.CASCADE,
        limit_choices_to={'tipo': 'OPERACIONES'}
    )
    estado = models.CharField(max_length=20, choices=EstadoVenezuela.choices)
    prefijo = models.CharField(max_length=3, unique=True)  # ZUL, CAR, etc.
    nombre = models.CharField(max_length=200)
    responsable = models.ForeignKey(User, on_delete=models.PROTECT)
    direccion = models.TextField()
    capacidad_maxima = models.PositiveIntegerField()
    activo = models.BooleanField(default=True)
```

### **Modelo: ActivoInventario (Producto Individual)**
```python
class ActivoInventario(SoftDeleteModel):
    """Cada producto individual con código único y trazabilidad"""
    
    class TipoActivo(models.TextChoices):
        BOMBA = 'BOMBA', 'Bomba'
        MOTOR = 'MOTOR', 'Motor'
        TUBERIA = 'TUBERIA', 'Tubería'
        QUIMICO = 'QUIMICO', 'Químico'
        ACCESORIO = 'ACCESORIO', 'Accesorio'
    
    class EstadoActivo(models.TextChoices):
        EN_ALMACEN = 'EN_ALMACEN', 'En Almacén'
        EN_TRANSITO = 'EN_TRANSITO', 'En Tránsito'
        INSTALADO = 'INSTALADO', 'Instalado'
        EN_USO = 'EN_USO', 'En Uso'
        MANTENIMIENTO = 'MANTENIMIENTO', 'En Mantenimiento'
        DADO_BAJA = 'DADO_BAJA', 'Dado de Baja'
    
    # Código único del activo
    codigo_activo = models.CharField(max_length=50, unique=True)
    codigo_original = models.CharField(max_length=50)  # Código sin prefijos adicionales
    
    # Información del producto
    tipo_activo = models.CharField(max_length=20, choices=TipoActivo.choices)
    producto_referencia = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE
    )
    producto_id = models.PositiveIntegerField()
    producto = GenericForeignKey('producto_referencia', 'producto_id')
    
    # Ubicación y estado actual
    almacen_actual = models.ForeignKey(
        'AlmacenRegional',
        on_delete=models.PROTECT,
        related_name='activos_actuales'
    )
    estado_actual = models.CharField(max_length=20, choices=EstadoActivo.choices)
    ubicacion_especifica = models.CharField(max_length=200, blank=True)
    
    # Información de origen
    almacen_origen = models.ForeignKey(
        'AlmacenRegional',
        on_delete=models.PROTECT,
        related_name='activos_originados'
    )
    fecha_ingreso_sistema = models.DateTimeField(auto_now_add=True)
    
    # Metadatos
    numero_serie = models.CharField(max_length=100, blank=True)
    numero_lote = models.CharField(max_length=100, blank=True)
    fecha_fabricacion = models.DateField(null=True, blank=True)
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    
    def generar_codigo_activo(self):
        """Genera código único del activo"""
        año = timezone.now().year
        secuencial = self._obtener_siguiente_secuencial()
        return f"{self.almacen_origen.prefijo}-{self.tipo_activo}-{secuencial:06d}-{año}"
    
    def actualizar_codigo_por_traslado(self, nuevo_almacen):
        """Actualiza código al trasladar a nuevo almacén"""
        if nuevo_almacen != self.almacen_actual:
            self.codigo_activo = f"{nuevo_almacen.prefijo}-{self.codigo_activo}"
```

### **Modelo: HistorialMovimientoActivo**
```python
class HistorialMovimientoActivo(models.Model):
    """Historial completo de movimientos de cada activo"""
    
    class TipoMovimiento(models.TextChoices):
        INGRESO_INICIAL = 'INGRESO_INICIAL', 'Ingreso Inicial'
        TRASLADO_ALMACEN = 'TRASLADO_ALMACEN', 'Traslado entre Almacenes'
        INSTALACION = 'INSTALACION', 'Instalación en Campo'
        RETIRO_MANTENIMIENTO = 'RETIRO_MANTENIMIENTO', 'Retiro para Mantenimiento'
        RETORNO_MANTENIMIENTO = 'RETORNO_MANTENIMIENTO', 'Retorno de Mantenimiento'
        BAJA_DEFINITIVA = 'BAJA_DEFINITIVA', 'Baja Definitiva'
    
    activo = models.ForeignKey(
        'ActivoInventario',
        on_delete=models.CASCADE,
        related_name='historial_movimientos'
    )
    
    # Información del movimiento
    tipo_movimiento = models.CharField(max_length=30, choices=TipoMovimiento.choices)
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    
    # Ubicaciones
    almacen_origen = models.ForeignKey(
        'AlmacenRegional',
        on_delete=models.PROTECT,
        related_name='movimientos_origen',
        null=True, blank=True
    )
    almacen_destino = models.ForeignKey(
        'AlmacenRegional',
        on_delete=models.PROTECT,
        related_name='movimientos_destino',
        null=True, blank=True
    )
    ubicacion_especifica_origen = models.CharField(max_length=200, blank=True)
    ubicacion_especifica_destino = models.CharField(max_length=200, blank=True)
    
    # Responsables del movimiento
    solicitado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='movimientos_solicitados'
    )
    aprobado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='movimientos_aprobados',
        null=True, blank=True
    )
    ejecutado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='movimientos_ejecutados',
        null=True, blank=True
    )
    recibido_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='movimientos_recibidos',
        null=True, blank=True
    )
    
    # Estados del movimiento
    estado_anterior = models.CharField(max_length=20)
    estado_nuevo = models.CharField(max_length=20)
    codigo_anterior = models.CharField(max_length=50)
    codigo_nuevo = models.CharField(max_length=50)
    
    # Información adicional
    motivo = models.TextField()
    observaciones = models.TextField(blank=True)
    documentos_adjuntos = models.JSONField(default=list, blank=True)
    
    # Metadatos de aprobación
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    fecha_ejecucion = models.DateTimeField(null=True, blank=True)
    fecha_recepcion = models.DateTimeField(null=True, blank=True)
```

### **Modelo: SolicitudTraslado**
```python
class SolicitudTraslado(models.Model):
    """Solicitudes de traslado entre almacenes"""
    
    class EstadoSolicitud(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        APROBADA_ORIGEN = 'APROBADA_ORIGEN', 'Aprobada por Origen'
        APROBADA_DESTINO = 'APROBADA_DESTINO', 'Aprobada por Destino'
        EN_TRANSITO = 'EN_TRANSITO', 'En Tránsito'
        COMPLETADA = 'COMPLETADA', 'Completada'
        RECHAZADA = 'RECHAZADA', 'Rechazada'
        CANCELADA = 'CANCELADA', 'Cancelada'
    
    # Información básica
    numero_solicitud = models.CharField(max_length=20, unique=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=EstadoSolicitud.choices, default='PENDIENTE')
    
    # Activos a trasladar
    activos = models.ManyToManyField('ActivoInventario', related_name='solicitudes_traslado')
    
    # Almacenes
    almacen_origen = models.ForeignKey(
        'AlmacenRegional',
        on_delete=models.PROTECT,
        related_name='solicitudes_origen'
    )
    almacen_destino = models.ForeignKey(
        'AlmacenRegional',
        on_delete=models.PROTECT,
        related_name='solicitudes_destino'
    )
    
    # Responsables
    solicitante = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='solicitudes_realizadas'
    )
    aprobador_origen = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='aprobaciones_origen',
        null=True, blank=True
    )
    aprobador_destino = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='aprobaciones_destino',
        null=True, blank=True
    )
    
    # Información del traslado
    motivo_traslado = models.TextField()
    fecha_programada = models.DateTimeField()
    prioridad = models.CharField(
        max_length=10,
        choices=[('BAJA', 'Baja'), ('MEDIA', 'Media'), ('ALTA', 'Alta'), ('URGENTE', 'Urgente')],
        default='MEDIA'
    )
    
    # Fechas de aprobación
    fecha_aprobacion_origen = models.DateTimeField(null=True, blank=True)
    fecha_aprobacion_destino = models.DateTimeField(null=True, blank=True)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    
    # Observaciones
    observaciones_origen = models.TextField(blank=True)
    observaciones_destino = models.TextField(blank=True)
    observaciones_traslado = models.TextField(blank=True)
    
    def generar_numero_solicitud(self):
        """Genera número único de solicitud"""
        año = timezone.now().year
        mes = timezone.now().month
        secuencial = SolicitudTraslado.objects.filter(
            fecha_solicitud__year=año,
            fecha_solicitud__month=mes
        ).count() + 1
        return f"ST-{año}{mes:02d}-{secuencial:04d}"
```

---

## 🔄 **Flujos de Proceso**

### **1. Flujo de Ingreso de Activo**
```python
def ingresar_activo_almacen(producto, almacen, responsable):
    """Ingresa un nuevo activo al sistema"""
    
    # 1. Crear activo con código único
    activo = ActivoInventario.objects.create(
        tipo_activo=determinar_tipo_activo(producto),
        producto=producto,
        almacen_actual=almacen,
        almacen_origen=almacen,
        estado_actual='EN_ALMACEN',
        valor_unitario=producto.precio_unitario
    )
    
    # 2. Generar código único
    activo.codigo_activo = activo.generar_codigo_activo()
    activo.codigo_original = activo.codigo_activo
    activo.save()
    
    # 3. Registrar en historial
    HistorialMovimientoActivo.objects.create(
        activo=activo,
        tipo_movimiento='INGRESO_INICIAL',
        almacen_destino=almacen,
        solicitado_por=responsable,
        aprobado_por=responsable,
        ejecutado_por=responsable,
        recibido_por=responsable,
        estado_anterior='NUEVO',
        estado_nuevo='EN_ALMACEN',
        codigo_anterior='',
        codigo_nuevo=activo.codigo_activo,
        motivo='Ingreso inicial al sistema'
    )
    
    return activo
```

### **2. Flujo de Solicitud de Traslado**
```python
def solicitar_traslado(activos, almacen_destino, solicitante, motivo):
    """Crea solicitud de traslado entre almacenes"""
    
    # 1. Validar que todos los activos estén en el mismo almacén origen
    almacen_origen = activos[0].almacen_actual
    if not all(activo.almacen_actual == almacen_origen for activo in activos):
        raise ValidationError("Todos los activos deben estar en el mismo almacén")
    
    # 2. Crear solicitud
    solicitud = SolicitudTraslado.objects.create(
        numero_solicitud=SolicitudTraslado().generar_numero_solicitud(),
        almacen_origen=almacen_origen,
        almacen_destino=almacen_destino,
        solicitante=solicitante,
        motivo_traslado=motivo,
        fecha_programada=timezone.now() + timedelta(days=7)
    )
    
    # 3. Asociar activos
    solicitud.activos.set(activos)
    
    # 4. Notificar a responsables
    notificar_solicitud_traslado(solicitud)
    
    return solicitud
```

### **3. Flujo de Aprobación y Ejecución**
```python
def aprobar_traslado(solicitud, aprobador, tipo_aprobacion):
    """Aprueba traslado (origen o destino)"""
    
    if tipo_aprobacion == 'ORIGEN':
        solicitud.aprobador_origen = aprobador
        solicitud.fecha_aprobacion_origen = timezone.now()
        solicitud.estado = 'APROBADA_ORIGEN'
        
    elif tipo_aprobacion == 'DESTINO':
        solicitud.aprobador_destino = aprobador
        solicitud.fecha_aprobacion_destino = timezone.now()
        solicitud.estado = 'APROBADA_DESTINO'
        
        # Si ambas aprobaciones están completas, ejecutar traslado
        if solicitud.aprobador_origen and solicitud.aprobador_destino:
            ejecutar_traslado(solicitud)
    
    solicitud.save()

def ejecutar_traslado(solicitud):
    """Ejecuta el traslado físico de activos"""
    
    for activo in solicitud.activos.all():
        # 1. Actualizar código del activo
        codigo_anterior = activo.codigo_activo
        activo.actualizar_codigo_por_traslado(solicitud.almacen_destino)
        
        # 2. Cambiar ubicación y estado
        activo.almacen_actual = solicitud.almacen_destino
        activo.estado_actual = 'EN_TRANSITO'
        activo.save()
        
        # 3. Registrar en historial
        HistorialMovimientoActivo.objects.create(
            activo=activo,
            tipo_movimiento='TRASLADO_ALMACEN',
            almacen_origen=solicitud.almacen_origen,
            almacen_destino=solicitud.almacen_destino,
            solicitado_por=solicitud.solicitante,
            aprobado_por=solicitud.aprobador_origen,
            estado_anterior='EN_ALMACEN',
            estado_nuevo='EN_TRANSITO',
            codigo_anterior=codigo_anterior,
            codigo_nuevo=activo.codigo_activo,
            motivo=solicitud.motivo_traslado
        )
    
    solicitud.estado = 'EN_TRANSITO'
    solicitud.save()
```

---

## 📊 **APIs y Endpoints**

### **Endpoints de Trazabilidad**
```python
# Historial completo de un activo
GET /api/activos/{codigo_activo}/historial/

# Ubicación actual de un activo
GET /api/activos/{codigo_activo}/ubicacion/

# Buscar activos por código o características
GET /api/activos/buscar/?q={codigo_o_criterio}

# Solicitar traslado
POST /api/traslados/solicitar/

# Aprobar traslado
POST /api/traslados/{id}/aprobar/

# Confirmar recepción
POST /api/traslados/{id}/confirmar-recepcion/
```

### **Reportes de Trazabilidad**
```python
# Inventario por almacén
GET /api/reportes/inventario-almacen/{almacen_id}/

# Activos en tránsito
GET /api/reportes/activos-transito/

# Historial de movimientos por período
GET /api/reportes/movimientos/?fecha_inicio={}&fecha_fin={}

# Activos por estado
GET /api/reportes/activos-por-estado/
```

---

## 🎯 **Beneficios del Sistema**

### **✅ Trazabilidad Completa**
- Cada activo tiene un código único e inmutable
- Historial completo desde origen hasta destino final
- Seguimiento en tiempo real de ubicación y estado

### **✅ Control de Inventario**
- Inventario exacto por almacén regional
- Prevención de pérdidas y extravíos
- Auditoría completa de movimientos

### **✅ Flujo de Aprobación**
- Doble aprobación para traslados
- Responsabilidades claras y trazables
- Notificaciones automáticas

### **✅ Reportes y Analytics**
- Dashboards por almacén regional
- Métricas de rotación de inventario
- Análisis de patrones de movimiento

---

**Este sistema garantiza la trazabilidad completa de todos los activos de Hidroven, manteniendo un control riguroso sobre los 9 almacenes regionales y proporcionando visibilidad total del ciclo de vida de cada producto.**