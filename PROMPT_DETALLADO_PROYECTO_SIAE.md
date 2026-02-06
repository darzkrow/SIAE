# Prompt Detallado para Generar el Proyecto SIAE

## Descripción General del Proyecto

Crea un **Sistema Integral de Administración de Equipos (SIAE)** para la gestión de inventario de activos hidrológicos, específicamente diseñado para empresas de agua potable y saneamiento como Hidroven. El sistema debe ser una aplicación web completa con backend Django REST Framework y frontend React.

## Arquitectura del Sistema

### Stack Tecnológico
- **Backend**: Django 5.0.2 + Django REST Framework 3.15.1
- **Frontend**: React 18.2.0 + Vite + TailwindCSS
- **Base de Datos**: PostgreSQL 15 (SQLite para desarrollo)
- **Cache/Queue**: Redis 7 + Celery 5.3.6
- **Contenedores**: Docker + Docker Compose
- **Proxy**: Nginx
- **Autenticación**: JWT con SimpleJWT
- **Documentación API**: Swagger/OpenAPI con drf-spectacular

### Estructura de Aplicaciones Django

#### 1. App `accounts` - Sistema de Usuarios y Permisos
```python
# Modelos principales:
- CustomUser (AbstractUser extendido)
- Role (roles dinámicos)
- Permission (permisos granulares)
- RolePermission (relación roles-permisos)
- UserRole (asignación de roles a usuarios)

# Características:
- Autenticación JWT
- Sistema de roles dinámico (ADMIN, OPERADOR, SUPERVISOR)
- Permisos granulares por modelo y acción
- Gestión de usuarios con metadatos adicionales
```

#### 2. App `inventario` - Gestión de Inventario Principal
```python
# Modelos base abstractos:
- ProductBase (clase abstracta para todos los productos)
- SoftDeleteModel (eliminación lógica)

# Productos especializados:
- Pipe (tuberías): material, diámetro, presión, longitud_unitaria
- PumpAndMotor (bombas y motores): potencia, voltaje, caudal, eficiencia
- Accessory (accesorios): tipo, subtipo, conexiones, presión_trabajo
- ChemicalProduct (químicos): concentración, peligrosidad, fecha_vencimiento

# Stocks por tipo:
- StockPipe: cantidad + metros_totales calculados
- StockPumpAndMotor: cantidad + estado_operativo
- StockAccessory: cantidad decimal
- StockChemical: cantidad por lote + vencimiento

# Movimientos:
- MovimientoInventario: ENTRADA, SALIDA, TRANSFER, AJUSTE
- InventoryAudit: auditoría completa de cambios
- Validaciones automáticas de stock

# Modelos auxiliares:
- Tag (etiquetas para organización)
- UnitOfMeasure (unidades de medida normalizadas)
- Supplier (proveedores)
```

#### 3. App `geography` - Ubicaciones Geográficas
```python
# Modelos:
- State (estados/provincias)
- Municipality (municipios)
- Parish (parroquias)
- Ubicacion (ubicaciones específicas: ALMACEN, INSTALACION)

# Características:
- Jerarquía geográfica completa
- Integración con ubicaciones de stock
- Soporte para múltiples países
```

#### 4. App `institucion` - Estructura Organizacional
```python
# Modelos:
- OrganizacionCentral (organización matriz)
- Sucursal (sucursales/oficinas)
- Acueducto (sistemas de agua específicos)

# Características:
- Jerarquía organizacional usando django-mptt
- Relación con ubicaciones geográficas
- Gestión de activos por organización
```

#### 5. App `catalogo` - Catálogos Maestros
```python
# Modelos:
- CategoriaProducto (categorías de productos)
- Marca (marcas de productos)
- Proveedor (información de proveedores)

# Características:
- Catálogos centralizados
- Eliminación lógica
- Validaciones de integridad
```

#### 6. App `compras` - Gestión de Compras
```python
# Modelos:
- OrdenCompra (órdenes de compra)
- ItemOrden (items de órdenes)

# Características:
- Integración con movimientos de inventario
- Flujo de aprobaciones
- Trazabilidad completa
```

#### 7. App `auditoria` - Sistema de Auditoría
```python
# Modelos:
- AuditLog (registro de cambios)
- SoftDeleteModel (clase base para eliminación lógica)

# Características:
- Auditoría automática de todos los cambios
- Middleware para captura de contexto
- Trazabilidad completa de operaciones
```

#### 8. App `notificaciones` - Sistema de Notificaciones
```python
# Modelos:
- Notificacion (notificaciones del sistema)
- Alerta (alertas de stock bajo)

# Características:
- Notificaciones en tiempo real con WebSockets
- Alertas automáticas de stock
- Integración con Celery para tareas asíncronas
```

## Funcionalidades Principales del Sistema

### 1. Gestión de Inventario
- **CRUD completo** de productos especializados (tuberías, bombas, accesorios, químicos)
- **Control de stock** en tiempo real por ubicación
- **Movimientos transaccionales**: entrada, salida, transferencia, ajuste
- **Validaciones automáticas** de stock disponible
- **Auditoría completa** de todos los cambios
- **Búsqueda avanzada** con filtros múltiples
- **Códigos únicos** generados automáticamente (SKU)

### 2. Sistema de Ubicaciones
- **Jerarquía geográfica**: Estado → Municipio → Parroquia
- **Ubicaciones específicas**: Almacenes e Instalaciones
- **Stock por ubicación** con transferencias entre ubicaciones
- **Compatibilidad legacy** con sistema anterior

### 3. Reportes y Estadísticas
- **Dashboard en tiempo real** con métricas clave
- **Reportes de stock** por ubicación y categoría
- **Movimientos históricos** con filtros avanzados
- **Alertas de stock bajo** configurables
- **Exportación de datos** en múltiples formatos
- **Gráficos interactivos** con Chart.js

### 4. Seguridad y Permisos
- **Autenticación JWT** con refresh tokens
- **Sistema de roles dinámico** configurable
- **Permisos granulares** por modelo y acción
- **Rate limiting** para prevenir abuso
- **CORS configurado** por entorno
- **Validación de entrada** en todos los endpoints

### 5. API REST Completa
- **Documentación automática** con Swagger/OpenAPI
- **Endpoints RESTful** para todas las operaciones
- **Paginación automática** en listados
- **Filtros avanzados** con django-filter
- **Serializers optimizados** con validaciones
- **Versionado de API** preparado

## Configuración del Frontend React

### Estructura de Componentes
```javascript
src/
├── components/
│   ├── adminlte/          // Componentes AdminLTE
│   ├── forms/             // Formularios especializados
│   ├── Sidebar.jsx        // Navegación lateral
│   └── StatCard.jsx       // Tarjetas de estadísticas
├── pages/
│   ├── Dashboard.jsx      // Panel principal
│   ├── Articulos.jsx      // Gestión de productos
│   ├── Stock.jsx          // Gestión de stock
│   ├── Movimientos.jsx    // Movimientos de inventario
│   ├── Reportes.jsx       // Reportes y estadísticas
│   ├── Compras.jsx        // Gestión de compras
│   ├── Auditoria.jsx      // Logs de auditoría
│   └── ErrorPage.jsx      // Páginas de error
├── context/
│   ├── AuthContext.jsx    // Contexto de autenticación
│   └── ThemeContext.jsx   // Tema claro/oscuro
├── services/
│   ├── api.js             // Cliente API base
│   └── inventory.service.js // Servicios de inventario
└── styles/
    └── dark-theme.css     // Estilos tema oscuro
```

### Características del Frontend
- **Lazy loading** de componentes para optimización
- **Tema claro/oscuro** persistente
- **Responsive design** con TailwindCSS
- **Validación en tiempo real** de formularios
- **Notificaciones toast** con SweetAlert2
- **Gráficos interactivos** con Chart.js y Recharts
- **Manejo de errores** con páginas específicas
- **Context API** para estado global

## Configuración de Docker

### docker-compose.yml
```yaml
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: gsih_inventario
      POSTGRES_USER: gsih_user
      POSTGRES_PASSWORD: gsih_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://gsih_user:gsih_password@db:5432/gsih_inventario
      - REDIS_HOST=redis
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    expose:
      - "8000"

  worker:
    build: ./backend
    command: celery -A config worker --loglevel=info
    depends_on:
      - db
      - redis

  nginx:
    build: ./nginx
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
```

## Especificaciones Técnicas Detalladas

### Modelos de Datos Especializados

#### Tuberías (Pipe)
```python
class Pipe(ProductBase):
    material = models.CharField(max_length=50)  # PVC, Acero, etc.
    diametro = models.DecimalField(max_digits=8, decimal_places=2)
    presion_trabajo = models.DecimalField(max_digits=8, decimal_places=2)
    longitud_unitaria = models.DecimalField(max_digits=8, decimal_places=2)
    tipo_union = models.CharField(max_length=50)
    tipo_uso = models.CharField(max_length=50)
```

#### Bombas y Motores (PumpAndMotor)
```python
class PumpAndMotor(ProductBase):
    # Identificación
    numero_serie = models.CharField(max_length=100, unique=True)
    modelo = models.CharField(max_length=100)
    
    # Especificaciones eléctricas
    potencia_hp = models.DecimalField(max_digits=8, decimal_places=2)
    potencia_kw = models.DecimalField(max_digits=8, decimal_places=2)
    voltaje = models.DecimalField(max_digits=8, decimal_places=2)
    fases = models.IntegerField()
    frecuencia = models.DecimalField(max_digits=5, decimal_places=1)
    
    # Especificaciones hidráulicas
    caudal_nominal = models.DecimalField(max_digits=10, decimal_places=2)
    altura_manometrica = models.DecimalField(max_digits=8, decimal_places=2)
    eficiencia = models.DecimalField(max_digits=5, decimal_places=2)
```

### Sistema de Movimientos Transaccionales
```python
class MovimientoInventario(models.Model):
    class TipoMovimiento(models.TextChoices):
        ENTRADA = 'ENTRADA', 'Entrada'
        SALIDA = 'SALIDA', 'Salida'
        TRANSFER = 'TRANSFER', 'Transferencia'
        AJUSTE = 'AJUSTE', 'Ajuste'
    
    # Relación genérica al producto
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    producto = GenericForeignKey('content_type', 'object_id')
    
    tipo = models.CharField(max_length=20, choices=TipoMovimiento.choices)
    cantidad = models.DecimalField(max_digits=15, decimal_places=4)
    
    # Ubicaciones
    ubicacion_origen = models.ForeignKey(Ubicacion, null=True, blank=True, 
                                       related_name='movimientos_origen')
    ubicacion_destino = models.ForeignKey(Ubicacion, null=True, blank=True,
                                        related_name='movimientos_destino')
    
    # Metadatos
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)
    
    def clean(self):
        # Validaciones de negocio
        if self.tipo == 'ENTRADA' and not self.ubicacion_destino:
            raise ValidationError("Entrada requiere ubicación destino")
        if self.tipo == 'SALIDA' and not self.ubicacion_origen:
            raise ValidationError("Salida requiere ubicación origen")
        if self.tipo == 'TRANSFER' and (not self.ubicacion_origen or not self.ubicacion_destino):
            raise ValidationError("Transferencia requiere origen y destino")
```

### Sistema de Auditoría Automática
```python
class AuditMiddleware:
    """Middleware para capturar automáticamente cambios en modelos."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Capturar contexto del usuario
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Activar auditoría para esta request
            pass
        
        response = self.get_response(request)
        return response
```

## Endpoints API Principales

### Autenticación
```
POST /api/accounts/login/          # Login con JWT
POST /api/accounts/logout/         # Logout
GET  /api/accounts/me/             # Perfil usuario actual
POST /api/accounts/refresh/        # Refresh token
```

### Inventario
```
GET/POST /api/pipes/               # Tuberías
GET/POST /api/pumps/               # Bombas y motores
GET/POST /api/accessories/         # Accesorios
GET/POST /api/chemicals/           # Productos químicos
GET/POST /api/stock/               # Stock general
GET/POST /api/movimientos/         # Movimientos
```

### Reportes
```
GET /api/reportes/dashboard/       # Estadísticas dashboard
GET /api/reportes/stock-ubicacion/ # Stock por ubicación
GET /api/reportes/movimientos/     # Reporte movimientos
GET /api/reportes/alertas/         # Alertas stock bajo
```

### Administración
```
GET/POST /api/ubicaciones/         # Ubicaciones
GET/POST /api/categorias/          # Categorías
GET/POST /api/proveedores/         # Proveedores
GET/POST /api/usuarios/            # Usuarios
```

## Configuración de Desarrollo

### Variables de Entorno (.env)
```bash
# Django
DEBUG=True
SECRET_KEY=tu-secret-key-super-segura
ALLOWED_HOSTS=localhost,127.0.0.1,backend

# Database
DATABASE_URL=postgresql://gsih_user:gsih_password@localhost:5432/gsih_inventario

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# CORS
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60  # minutos
JWT_REFRESH_TOKEN_LIFETIME=7  # días
```

### Comandos de Inicialización
```bash
# Backend
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
python manage.py loaddata fixtures/initial_data.json

# Frontend
npm install
npm run dev

# Docker
docker-compose up --build
```

## Testing y Calidad

### Tests Backend (pytest + hypothesis)
```python
# Tests unitarios
pytest inventario/tests/test_models.py
pytest inventario/tests/test_api.py

# Tests de propiedades (property-based testing)
pytest inventario/tests/test_properties.py

# Coverage
pytest --cov=inventario --cov-report=html
```

### Tests Frontend (Vitest)
```bash
npm run test              # Tests unitarios
npm run test:coverage     # Coverage report
npm run test:ui           # UI interactiva
```

## Características de Producción

### Seguridad
- Rate limiting (100/hora anónimo, 1000/hora autenticado)
- CORS configurado por entorno
- Validación de entrada en todos los endpoints
- Encriptación de contraseñas con bcrypt
- Tokens JWT con expiración configurable
- Middleware de auditoría automática

### Performance
- Connection pooling en PostgreSQL
- Select/Prefetch related para evitar N+1 queries
- Paginación automática en listados
- Índices de base de datos optimizados
- Multi-stage Docker builds
- Compresión gzip en Nginx

### Monitoreo
- Health checks en Docker
- Logs estructurados
- Métricas de performance
- Alertas automáticas de stock
- Dashboard de estadísticas en tiempo real

## Documentación Requerida

### Archivos de Documentación
```
docs/
├── README.md                    # Documentación principal
├── ARQUITECTURA-BACKEND.md      # Arquitectura técnica
├── COMIENZA-AQUI.md            # Guía de inicio rápido
├── DEPLOYMENT.md               # Guía de despliegue
├── api/
│   ├── INVENTARIO.md           # Endpoints inventario
│   ├── ACCOUNTS.md             # Endpoints usuarios
│   └── REPORTES.md             # Endpoints reportes
└── plantillas_importacion/     # Templates CSV
```

### Swagger/OpenAPI
- Documentación automática en `/api/docs/`
- Ejemplos de requests/responses
- Esquemas de validación
- Códigos de error documentados

## Comandos de Gestión Django

### Comandos Personalizados
```python
# management/commands/setup_initial_data.py
class Command(BaseCommand):
    def handle(self, *args, **options):
        # Crear datos iniciales
        # Categorías, ubicaciones, usuarios por defecto
        pass

# management/commands/check_stock_alerts.py
class Command(BaseCommand):
    def handle(self, *args, **options):
        # Verificar alertas de stock bajo
        # Enviar notificaciones
        pass
```

## Especificaciones de UI/UX

### Tema y Diseño
- **AdminLTE 3.2** como base de diseño
- **TailwindCSS** para estilos personalizados
- **Tema claro/oscuro** con persistencia
- **Responsive design** para móviles y tablets
- **Iconos Lucide React** consistentes

### Componentes Clave
- Dashboard con gráficos en tiempo real
- Formularios con validación instantánea
- Tablas con paginación y filtros
- Modales para acciones rápidas
- Notificaciones toast no intrusivas
- Sidebar colapsible con navegación

### Flujos de Usuario
1. **Login** → Dashboard con métricas
2. **Gestión de productos** → CRUD con validaciones
3. **Movimientos** → Formulario guiado con validaciones de stock
4. **Reportes** → Filtros avanzados y exportación
5. **Administración** → Gestión de usuarios y configuración

## Criterios de Aceptación

### Funcionalidad
- [ ] CRUD completo de todos los tipos de productos
- [ ] Sistema de movimientos transaccionales funcionando
- [ ] Validaciones automáticas de stock
- [ ] Reportes y dashboard con datos reales
- [ ] Sistema de permisos granular
- [ ] API REST completamente documentada

### Performance
- [ ] Tiempo de respuesta API < 200ms
- [ ] Bundle frontend < 500KB
- [ ] Imagen Docker < 500MB
- [ ] Score Lighthouse ≥ 90

### Seguridad
- [ ] Autenticación JWT implementada
- [ ] Rate limiting configurado
- [ ] Validación de entrada en todos los endpoints
- [ ] CORS configurado correctamente
- [ ] Auditoría de cambios funcionando

### Testing
- [ ] Coverage backend ≥ 70%
- [ ] Tests unitarios para modelos críticos
- [ ] Tests de API para endpoints principales
- [ ] Tests de integración para flujos completos

## Entregables Finales

1. **Código fuente completo** con estructura descrita
2. **Base de datos** con migraciones y datos de prueba
3. **Documentación técnica** completa
4. **Configuración Docker** lista para producción
5. **Tests automatizados** con coverage adecuado
6. **API documentada** con Swagger
7. **Manual de usuario** básico
8. **Guía de despliegue** paso a paso

---

**Nota**: Este prompt está diseñado para generar un sistema completo y funcional. Asegúrate de implementar todas las validaciones de negocio, manejar errores apropiadamente, y seguir las mejores prácticas de Django y React. El sistema debe ser escalable, mantenible y seguro para uso en producción.