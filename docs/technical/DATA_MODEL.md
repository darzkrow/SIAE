# Modelo de Datos y Relaciones 📊

El esquema de datos de SIAE está diseñado para maximizar la integridad referencial y permitir una trazabilidad de 360 grados.

## 📐 Diagrama de Entidad-Relación (Simplificado)

```mermaid
erDiagram
    UBICACION ||--o{ STOCK : almacena
    PRODUCTO ||--o{ STOCK : tiene
    PRODUCTO ||--o{ ACTIVO_FIJO : es_un
    SUPPLIER ||--o{ PRODUCTO : provee
    STOCK ||--o{ MOVIMIENTO : genera
    MOVIMIENTO ||--o{ AUDITORIA : registra

    PRODUCTO {
        string sku
        string nombre
        fk unidad_medida
        fk categoria
    }
    
    STOCK {
        decimal cantidad
        string lote
        fk producto
        fk ubicacion
    }
    
    ACTIVO_FIJO {
        string codigo_activo
        date fecha_adquisicion
        int vida_util
    }
```

## 🔑 Conceptos Clave

### 🏷️ Normalización de Productos
A diferencia de sistemas genéricos, SIAE desglosa los productos en jerarquías funcionales (Químicos, Tuberías, Equipos) que heredan de una base común pero mantienen campos técnicos específicos para la industria hídrica.

### 📍 Gestión de Ubicaciones
Las ubicaciones están vinculadas a la estructura geográfica nacional, permitiendo reportes agregados por Parroquia, Municipio o Estado.

### 🔄 Trazabilidad de Movimientos
Cada cambio en el stock físico se registra como un `MovimientoInventario`. Este registro es inmutable y está vinculado a un reporte de auditoría que captura el estado del sistema en el momento de la transacción.

### 🛡️ Soft Delete
La mayoría de los modelos de negocio implementan `SoftDeleteModel`. Esto significa que los registros nunca se borran físicamente de la base de datos, sino que se marcan como inactivos, preservando la integridad histórica de los reportes.
