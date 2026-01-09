# TAREAS PARA COMPLETAR PROYECTO GSIH - INVENTARIO

## 🔴 PRIORIDAD CRÍTICA (Funcionalidad Básica)

### Backend - API Faltante
- [x] **Crear endpoint de auditoría** (`/api/audits/`) ✅ COMPLETADO
  - [x] Crear `InventoryAuditViewSet` con filtros por status, tipo_movimiento, fecha
  - [x] Agregar serializer para `InventoryAudit`
  - [x] Incluir en URLs

- [x] **Implementar permisos por rol** ✅ COMPLETADO
  - [x] Crear `permission_classes` personalizadas para ADMIN vs OPERADOR
  - [x] Restringir operadores a su sucursal asignada
  - [x] Implementar aprobación de movimientos críticos

- [x] **Crear endpoint de estadísticas** (`/api/reportes/`) ✅ COMPLETADO
  - [x] Stock por sucursal/acueducto
  - [x] Movimientos por período
  - [x] Alertas activas
  - [x] Artículos con stock bajo

- [x] **Configurar alertas de email** ✅ COMPLETADO
  - [x] Agregar `STOCK_ALERT_EMAILS` y `DEFAULT_FROM_EMAIL` en settings.py
  - [x] Configurar SMTP para envío de notificaciones

### Frontend - Módulos Principales
- [x] **Crear sistema de navegación** ✅ COMPLETADO
  - [x] Sidebar con menú principal
  - [x] Router con rutas protegidas
  - [x] Breadcrumbs para navegación

- [x] **Módulo de Movimientos de Inventario** ✅ COMPLETADO
  - [x] Página para crear movimientos (ENTRADA/SALIDA/TRANSFERENCIA/AJUSTE)
  - [x] Formulario con validación de stock
  - [x] Lista de movimientos con filtros
  - [x] Detalle de movimiento con auditoría

- [x] **Módulo de Gestión de Stock** ✅ COMPLETADO
  - [x] Vista de stock por acueducto
  - [x] Búsqueda de artículos
  - [x] Alertas de stock bajo
  - [x] Transferencias entre acueductos

- [ ] **Módulo de Artículos**
  - CRUD de tuberías con filtros por material/diámetro
  - CRUD de equipos con búsqueda por marca/modelo
  - Categorías de artículos

### Integración Backend-Frontend
- [x] **Endpoint de perfil de usuario** (`/api/accounts/me/`) ✅ COMPLETADO
  - [x] Validar token y retornar datos del usuario
  - [x] Incluir permisos y sucursal asignada

- [x] **Interceptor de autenticación en frontend** ✅ COMPLETADO
  - [x] Manejar errores 401/403 automáticamente
  - [x] Redirigir a login si token inválido
  - [x] Refresh automático de token

## 🟡 PRIORIDAD ALTA (Funcionalidad Avanzada)

### Backend - Mejoras de API
- [x] **Agregar filtros y búsqueda a ViewSets** ✅ COMPLETADO
  - [x] Filtros por fecha, tipo, sucursal en movimientos
  - [x] Búsqueda en tuberías por material/diámetro
  - [x] Búsqueda en equipos por marca/modelo/serie
  - [x] Paginación personalizada

- [ ] **Endpoint de búsqueda de stock** (`/api/stock-search/`)
  - Consultar stock de artículo específico por ubicación
  - Disponibilidad para transferencias
  - Historial de movimientos por artículo

- [ ] **Validaciones adicionales**
  - CheckConstraints en base de datos para stock >= 0
  - Validación de números de serie únicos
  - Restricciones de transferencia entre sucursales

### Frontend - Funcionalidades Avanzadas
- [ ] **Módulo de Reportes**
  - Reporte de movimientos por período
  - Reporte de stock por sucursal
  - Exportación a CSV/PDF
  - Gráficos de tendencias

- [ ] **Módulo de Alertas**
  - Configuración de umbrales de stock
  - Panel de notificaciones
  - Historial de alertas
  - Configuración de destinatarios de email

- [ ] **Gestión de Usuarios** (para ADMIN)
  - CRUD de usuarios
  - Asignación de roles y sucursales
  - Permisos granulares

### Docker y Deployment
- [ ] **Corregir Dockerfile del frontend**
  - Agregar `npm install` en build
  - Optimizar para producción con multi-stage build
  - Configurar variables de entorno correctamente

- [ ] **Mejorar docker-compose para producción**
  - Agregar PostgreSQL como base de datos
  - Script de inicialización con migraciones y seed
  - Variables de entorno seguras
  - Health checks

## 🟢 PRIORIDAD MEDIA (Mejoras de UX/UI)

### Frontend - Experiencia de Usuario
- [ ] **Mejorar validación de formularios**
  - Validación en tiempo real
  - Mensajes de error específicos
  - Feedback visual de estados

- [ ] **Estados de carga y errores**
  - Spinners y skeletons
  - Retry automático en errores de red
  - Notificaciones toast para acciones

- [ ] **Responsive design completo**
  - Optimización para móviles
  - Tablas responsive con scroll horizontal
  - Menú hamburguesa en mobile

- [ ] **Dashboard mejorado**
  - Gráficos de stock por categoría
  - Alertas recientes
  - Accesos rápidos contextuales
  - Widgets configurables

### Backend - Optimizaciones
- [ ] **Logging y monitoreo**
  - Logging de operaciones críticas
  - Métricas de performance
  - Alertas de sistema

- [ ] **Caché y performance**
  - Caché de consultas frecuentes
  - Optimización de queries con select_related
  - Índices de base de datos

## 🎯 ROADMAP SUGERIDO

### Fase 1 (2-3 semanas): MVP Funcional ✅ COMPLETADO
1. [x] Crear navegación y estructura del frontend
2. [x] Implementar módulo de movimientos básico
3. [x] Agregar endpoint de auditoría
4. [x] Corregir Docker para desarrollo

### Fase 2 (2-3 semanas): Funcionalidad Completa (EN PROGRESO)
1. [ ] Completar módulos de stock y artículos
2. [ ] Implementar permisos por rol
3. [ ] Agregar reportes básicos
4. [ ] Mejorar validaciones

### Fase 3 (2-3 semanas): Producción Ready
1. [ ] Configurar PostgreSQL y nginx
2. [ ] Implementar alertas y notificaciones
3. [ ] Optimizar performance
4. [ ] Documentación completa

### Fase 4 (1-2 semanas): Funcionalidades Avanzadas
1. [ ] Sistema de aprobaciones
2. [ ] Integración con sistemas externos
3. [ ] Auditoría avanzada
4. [ ] Mejoras de UX/UI