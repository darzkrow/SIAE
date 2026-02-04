# 📋 Prompt para Análisis de Estructura del Proyecto SIAE

## 🎯 Objetivo
Analizar la estructura organizacional y arquitectónica del Sistema de Inventario de Activos Estratégicos (SIAE) para entender su organización actual y preparar una nueva estructura optimizada.

## 🏗️ Arquitectura General

### **Stack Tecnológico**
- **Backend**: Django 4.x + Django REST Framework
- **Frontend**: React 18 + Vite + AdminLTE3
- **Base de Datos**: PostgreSQL (producción) / SQLite (desarrollo)
- **Containerización**: Docker + Docker Compose
- **Proxy**: Nginx
- **Cache/Queue**: Redis + Celery
- **WebSockets**: Django Channels
- **Testing**: Pytest + Hypothesis (PBT) + Vitest
- **Documentación API**: drf-spectacular (OpenAPI/Swagger)

### **Patrón Arquitectónico**
- **Backend**: Arquitectura por Apps Django (Modular)
- **Frontend**: SPA con React Router + Context API
- **API**: RESTful con DRF ViewSets
- **Autenticación**: JWT + Session-based
- **Permisos**: Role-based (ADMIN/OPERADOR)

## 📁 Estructura de Directorios

```
SIAE/
├── 🔧 Configuración Raíz
│   ├── docker-compose.yml          # Orquestación de servicios
│   ├── docker-compose.prod.yml     # Configuración producción
│   ├── nginx.conf                  # Configuración proxy
│   ├── .env                        # Variables de entorno
│   └── README.md                   # Documentación principal
│
├── 🐍 Backend (Django)
│   ├── config/                     # Configuración Django
│   │   ├── settings.py            # Settings principal
│   │   ├── urls.py                # URLs globales
│   │   ├── wsgi.py/asgi.py        # Servidores web
│   │   └── celery.py              # Configuración Celery
│   │
│   ├── 👥 Apps de Negocio
│   │   ├── accounts/              # Autenticación y usuarios
│   │   ├── inventario/            # Core - Gestión inventario
│   │   ├── catalogo/              # Categorías y marcas
│   │   ├── compras/               # Órdenes de compra
│   │   ├── auditoria/             # Logs y auditoría
│   │   ├── notificaciones/        # Sistema notificaciones
│   │   ├── institucion/           # Organizaciones/Sucursales
│   │   └── geography/             # Ubicaciones geográficas
│   │
│   ├── 📋 Estructura por App
│   │   ├── models.py              # Modelos de datos
│   │   ├── views.py               # ViewSets API
│   │   ├── serializers.py         # Serializers DRF
│   │   ├── urls.py                # URLs de la app
│   │   ├── admin.py               # Admin Django
│   │   ├── permissions.py         # Permisos custom
│   │   ├── filters.py             # Filtros DRF
│   │   ├── tests/                 # Tests unitarios
│   │   └── migrations/            # Migraciones DB
│   │
│   └── 🔧 Archivos de Soporte
│       ├── requirements.txt       # Dependencias Python
│       ├── manage.py              # CLI Django
│       ├── pytest.ini            # Configuración tests
│       └── Dockerfile.backend     # Imagen Docker
│
├── ⚛️ Frontend (React)
│   ├── src/
│   │   ├── 📄 Páginas
│   │   │   ├── Dashboard.jsx      # Panel principal
│   │   │   ├── Login.jsx          # Autenticación
│   │   │   ├── Articulos.jsx      # Gestión productos
│   │   │   ├── Stock.jsx          # Control stock
│   │   │   ├── Movimientos.jsx    # Movimientos inventario
│   │   │   ├── Reportes.jsx       # Reportes y analytics
│   │   │   ├── Usuarios.jsx       # Gestión usuarios
│   │   │   └── [otras páginas]
│   │   │
│   │   ├── 🧩 Componentes
│   │   │   ├── adminlte/          # Componentes AdminLTE3
│   │   │   ├── forms/             # Formularios reutilizables
│   │   │   ├── Layout.jsx         # Layout principal
│   │   │   ├── Sidebar.jsx        # Navegación lateral
│   │   │   └── ThemeSettings.jsx  # Configuración tema
│   │   │
│   │   ├── 🔄 Context & Services
│   │   │   ├── context/
│   │   │   │   ├── AuthContext.jsx    # Estado autenticación
│   │   │   │   └── ThemeContext.jsx   # Estado tema
│   │   │   └── services/
│   │   │       └── inventory.service.js # API client
│   │   │
│   │   └── 🎨 Estilos
│   │       ├── index.css          # Estilos globales
│   │       └── dark-theme.css     # Tema oscuro
│   │
│   ├── public/                    # Archivos estáticos
│   ├── package.json              # Dependencias Node
│   ├── vite.config.js            # Configuración Vite
│   └── Dockerfile                # Imagen Docker
│
├── 🌐 Nginx
│   ├── Dockerfile                # Imagen proxy
│   └── nginx.conf               # Configuración servidor
│
├── 📚 Documentación
│   ├── docs/                    # Documentación técnica
│   │   ├── api/                 # Docs API por app
│   │   ├── ARQUITECTURA-BACKEND.md
│   │   ├── DEPLOYMENT.md
│   │   └── MANUAL-DE-USO.md
│   │
│   └── 📋 Archivos de Estado
│       ├── SYSTEM_FIXES_COMPLETE.md
│       ├── REPORTS_API_FIX.md
│       └── [otros archivos de estado]
│
└── 🔧 Herramientas
    ├── .kiro/specs/             # Especificaciones Kiro
    ├── docker/                  # Scripts Docker
    ├── ssl/                     # Certificados SSL
    └── venv/                    # Entorno virtual Python
```

## 🏛️ Arquitectura de Apps Django

### **Apps Principales**

1. **`accounts/`** - Gestión de Usuarios
   - CustomUser model con roles
   - Autenticación JWT/Session
   - Permisos por rol

2. **`inventario/`** - Core del Sistema
   - Modelos: Pipe, PumpAndMotor, ChemicalProduct, Accessory
   - Stock: StockPipe, StockPumpAndMotor, etc.
   - Movimientos: MovimientoInventario
   - ViewSets con funcionalidad avanzada

3. **`catalogo/`** - Categorización
   - CategoriaProducto, Marca
   - Datos maestros del sistema

4. **`institucion/`** - Estructura Organizacional
   - OrganizacionCentral, Sucursal, Acueducto
   - Jerarquía institucional

5. **`auditoria/`** - Trazabilidad
   - AuditLog para cambios
   - Middleware de auditoría
   - SoftDelete mixin

6. **`notificaciones/`** - Comunicación
   - Sistema de notificaciones
   - WebSocket consumers
   - Alertas de stock

7. **`geography/`** - Ubicaciones
   - Modelos geográficos
   - Estados, municipios, parroquias

8. **`compras/`** - Procurement
   - OrdenCompra, ItemOrden
   - Gestión de compras

## ⚛️ Arquitectura Frontend React

### **Estructura de Componentes**

```
src/
├── 📄 Pages (Rutas principales)
│   ├── Dashboard.jsx          # Panel con KPIs y widgets
│   ├── Login.jsx             # Autenticación
│   ├── Articulos.jsx         # CRUD productos
│   ├── Stock.jsx             # Control inventario
│   ├── Movimientos.jsx       # Transacciones
│   └── [12+ páginas más]
│
├── 🧩 Components
│   ├── adminlte/             # Wrapper AdminLTE3
│   │   ├── AdminLTELayout.jsx
│   │   ├── AdminLTEWidget.jsx
│   │   ├── AdminLTENavbar.jsx
│   │   └── AdminLTENotification.jsx
│   │
│   ├── forms/                # Formularios reutilizables
│   ├── Layout.jsx           # Layout base
│   ├── Sidebar.jsx          # Navegación
│   ├── ThemeSettings.jsx    # Configuración tema
│   └── ErrorBoundary.jsx    # Manejo errores
│
├── 🔄 Context (Estado Global)
│   ├── AuthContext.jsx      # Usuario, login, logout
│   └── ThemeContext.jsx     # Tema claro/oscuro
│
├── 🌐 Services (API)
│   └── inventory.service.js  # Cliente HTTP para API
│
└── 🎨 Styles
    ├── index.css            # Estilos base + Tailwind
    └── dark-theme.css       # Tema oscuro personalizado
```

### **Patrones de Estado**
- **Context API**: AuthContext, ThemeContext
- **Local State**: useState para componentes
- **Persistencia**: localStorage para tema y sesión

## 🔌 API y Endpoints

### **Estructura de URLs**
```
/api/
├── accounts/              # Autenticación
│   ├── login/
│   ├── logout/
│   └── me/
│
├── inventario/            # Core inventario
│   ├── tuberias/
│   ├── equipos/
│   ├── quimicos/
│   ├── accesorios/
│   ├── stock-*/
│   ├── movimientos/
│   └── reportes-v2/
│
├── catalog/               # Catálogo
│   ├── categorias/
│   └── marcas/
│
├── geography/             # Geografía
├── compras/              # Compras
├── auditoria/            # Auditoría
└── notificaciones/       # Notificaciones
```

### **Patrones de ViewSets**
- **ModelViewSet**: CRUD completo
- **ViewSet**: Endpoints custom
- **Mixins**: AuditMixin, TrashBinMixin
- **Permissions**: IsAdminOrReadOnly, IsAdminOrSameSucursal
- **Filters**: DjangoFilterBackend, SearchFilter

## 🗄️ Modelo de Datos

### **Entidades Principales**

1. **Productos**
   - Pipe (tuberías)
   - PumpAndMotor (bombas/motores)
   - ChemicalProduct (químicos)
   - Accessory (accesorios)

2. **Stock**
   - StockPipe, StockPumpAndMotor, etc.
   - Ubicación por acueducto
   - Control de cantidades

3. **Movimientos**
   - MovimientoInventario (Generic FK)
   - Tipos: ENTRADA, SALIDA, TRANSFERENCIA, AJUSTE
   - Trazabilidad completa

4. **Organización**
   - OrganizacionCentral → Sucursal → Acueducto
   - Jerarquía institucional

### **Patrones de Modelo**
- **Abstract Base Classes**: Para herencia
- **SoftDelete**: Borrado lógico
- **Audit Trail**: Trazabilidad automática
- **Generic Foreign Keys**: Flexibilidad relacional

## 🔧 Configuración y Deploy

### **Docker Compose Services**
- **db**: PostgreSQL 15
- **redis**: Cache y message broker
- **backend**: Django app
- **worker**: Celery worker
- **nginx**: Reverse proxy

### **Variables de Entorno**
- Database: `DATABASE_URL`
- Security: `SECRET_KEY`, `DEBUG`
- CORS: `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`
- Email: `EMAIL_HOST_*`
- Redis: `REDIS_HOST`

## 🧪 Testing y Calidad

### **Backend Testing**
- **Pytest**: Framework principal
- **Hypothesis**: Property-based testing
- **Coverage**: Objetivo 70%+
- **Fixtures**: Datos de prueba

### **Frontend Testing**
- **Vitest**: Framework de testing
- **Testing Library**: Componentes React
- **Fast-check**: Property-based testing JS

## 📊 Características Actuales

### ✅ **Implementado**
- Sistema completo de inventario
- Autenticación y permisos
- Dashboard con métricas
- Tema oscuro persistente
- API REST completa
- Documentación Swagger
- Docker deployment
- Auditoría y logs
- Notificaciones en tiempo real
- Reportes y analytics

### 🔄 **En Desarrollo** (Spec system-modernization)
- Sistema de permisos dinámico
- Búsqueda avanzada
- Exportación/importación
- Optimizaciones de rendimiento
- Tests de integración

## 🎯 Preguntas para Análisis

### **Arquitectura**
1. ¿La separación actual de apps Django es óptima?
2. ¿El frontend necesita mejor gestión de estado (Redux)?
3. ¿La estructura de componentes React es escalable?

### **Rendimiento**
1. ¿Hay cuellos de botella en las consultas DB?
2. ¿El bundle de frontend es óptimo?
3. ¿Se necesita más caching?

### **Mantenibilidad**
1. ¿El código está bien documentado?
2. ¿Los tests cubren casos críticos?
3. ¿La estructura facilita nuevas funcionalidades?

### **Escalabilidad**
1. ¿El sistema soporta múltiples organizaciones?
2. ¿La arquitectura permite microservicios futuros?
3. ¿El deployment es robusto para producción?

## 📋 Entregables Esperados

1. **Análisis de Estructura Actual**
   - Fortalezas y debilidades
   - Patrones identificados
   - Deuda técnica

2. **Propuesta de Nueva Estructura**
   - Reorganización de directorios
   - Mejores prácticas aplicadas
   - Justificación de cambios

3. **Plan de Migración**
   - Pasos para transición
   - Riesgos y mitigaciones
   - Timeline estimado

---

**Usa este prompt para analizar la estructura actual del proyecto SIAE y proponer mejoras organizacionales y arquitectónicas.**