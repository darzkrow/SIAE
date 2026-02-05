# Arquitectura Técnica SIAE 🏗️

SIAE implementa un diseño modular en el backend para separar las responsabilidades de negocio de forma clara y eficiente.

## 🧱 Estructura de Aplicaciones

### 1. `core`
La base funcional del sistema. No contiene lógica de negocio específica, sino herramientas transversales:
- **Modelos Base**: `SoftDeleteModel`, `TimeStampedModel`.
- **Permisos Dinámicos**: Control de acceso granular para administradores y aprobadores.
- **Filtros Avanzados**: Lógica de búsqueda facetada y vectores de búsqueda.

### 2. `productos`
Contiene la definición estática de lo que la institución maneja:
- **ProductBase**: Modelo abstracto para campos comunes (SKU, nombre, categoría).
- **Extensiones**: Modelos especializados para Químicos, Tuberías, Equipos y Accesorios.
- **UnitOfMeasure**: Gestión de magnitudes físicas.

### 3. `stock`
Gestiona el estado dinámico del inventario:
- **Stock**: Cantidades reales por ubicación y lote.
- **Movimientos**: Registro cronológico de transacciones.
- **Auditoría**: Logs detallados de errores o inconsistencias en los movimientos.

### 4. `activos`
Lógica para bienes de capital y mantenimiento:
- **ActivoFijo**: Gestión financiera y de ubicación de activos.
- **Ficha Técnica**: Datos operativos para motores y bombas.
- **Mantenimiento**: Historial de servicios.

### 5. `proveedores`
Aislado por requerimientos estratégicos:
- Gestión independiente de RIF, contactos y trazabilidad de origen de suministros.

### 6. `catalogo`
Repositorio central de taxonomía:
- Marcas, Categorías y Etiquetas unificadas para todo el sistema.

### 7. `geography`
Jerarquía de ubicación física:
- Estado -> Municipio -> Parroquia -> Ubicación (Almacén, Estación, Sede).

---

## 🛰️ Capa de Comunicación

### REST API
Utiliza Django REST Framework (DRF) con:
- **ViewSets**: Lógica CRUD estandarizada.
- **Serializers**: Validación y transformación de tipos de datos.

### WebSockets (Real-time)
Implementado vía Django Channels y Redis para:
- Notificaciones de aprobación de movimientos.
- Alertas críticas de stock.

---

## 🔍 Estrategia de Búsqueda
El sistema utiliza `SearchVectorField` de PostgreSQL para permitir búsquedas rápidas sobre campos de texto pesado (`nombre`, `descripcion`, `sku`, `rif`), optimizando el rendimiento mediante índices GIN.
