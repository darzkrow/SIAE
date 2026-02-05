# Guía de API y Endpoints 🔌

La API de SIAE está construida sobre Django REST Framework y sigue principios RESTful.

## 🔑 Autenticación
El sistema utiliza autenticación basada en JWT (JSON Web Tokens).
- **Endpoint**: `/api/token/`
- **Cabecera**: `Authorization: Bearer <TOKEN>`

---

## 🛤️ Endpoints Principales

### 📦 Productos e Inventario
| Endpoint | Método | Descripción |
|----------|---------|-------------|
| `/api/products/chemicals/` | GET/POST | Gestión de productos químicos |
| `/api/products/tuberias/` | GET/POST | Gestión de tuberías |
| `/api/products/equipos/` | GET/POST | Gestión de bombas y motores |
| `/api/stock/` | GET | Consulta de existencias por ubicación |
| `/api/stock/movements/` | POST | Creación de movimientos (Entrada/Salida/Transferencia) |

### 🏘️ Ubicaciones y Geografía
| Endpoint | Método | Descripción |
|----------|---------|-------------|
| `/api/geography/ubicaciones/` | GET | Listado de almacenes y estaciones |
| `/api/institucion/sucursales/` | GET | Listado de sucursales administrativas |

### 🛡️ Activos y Proveedores
| Endpoint | Método | Descripción |
|----------|---------|-------------|
| `/api/assets/` | GET/POST | Gestión de activos fijos |
| `/api/suppliers/` | GET/POST | Gestión de proveedores |

---

## 🔍 Funciones de Búsqueda y Filtrado

La mayoría de los listados (`GET`) soportan filtros avanzados:
- **Búsqueda General**: `?search=cloro`
- **Filtrado por Categoría**: `?categoria=<ID>`
- **Stock Bajo**: `?low_stock=true`

---

## ⚡ Notificaciones Real-time
El sistema envía señaes vía WebSockets en el path:
`ws://<host>/ws/notifications/`

Eventos soportados:
- `MOVEMENT_APPROVED`: Notificación al solicitante cuando se aprueba una transferencia.
- `LOW_STOCK_ALERT`: Alerta automática a administradores.
