# Plan de Pruebas y Documentación de API - SIAE

Este documento detalla el plan de pruebas del backend y el estado de la documentación de los endpoints.

## 📋 Lista de Tareas (Tasks) de Pruebas

### 🛡️ Pruebas de Auditoría y Soft Delete
- [x] **TC-AUD-01**: Verificar que al crear un producto (Químico) se genere un registro en `AuditLog`.
- [x] **TC-AUD-02**: Verificar que el middleware capture correctamente la IP y el Usuario en el log.
- [x] **TC-SOFT-01**: Verificar que al "eliminar" una Categoría, esta no desaparezca de la DB sino que marque `deleted_at`.
- [x] **TC-SOFT-02**: Verificar que los objetos en la papelera puedan ser restaurados.

### 📦 Pruebas de Inventario y Movimientos
- [ ] **TC-INV-01**: Verificar entrada de stock y actualización automática de cantidades.
- [ ] **TC-INV-02**: Verificar transferencia entre ubicaciones y validación de stock suficiente.
- [ ] **TC-INV-03**: Verificar que una salida sin stock devuelva error 400.

### 💰 Pruebas de Compras
- [ ] **TC-COM-01**: Verificar generación automática de correlativo de Orden de Compra (OC-2026-XXXXX).
- [ ] **TC-COM-02**: Verificar que una transferencia genere automáticamente una Orden de Compra vinculada.

### 🚨 Pruebas de Notificaciones
- [ ] **TC-NOT-01**: Verificar creación de alerta cuando el stock cae por debajo del umbral.

---

## 🛠️ Ejecución de Pruebas (Bitácora)
*(Se completará a medida que se ejecuten los tests)*

---

## 📖 Manual de Endpoints (Documentación Técnica)

### Estándares Globales
- **Formato**: JSON
- **Autenticación**: JWT Token (Bearer) requerido para todos los endpoints excepto login.
- **Códigos de Estado**:
  - `200/201`: Éxito.
  - `400`: Error de validación / Negocio.
  - `401/403`: No autorizado / Prohibido.
  - `404`: No encontrado.
  - `405`: Método no permitido (Restricción estricta).

---

### [Catálogo] Categorías de Productos
- **Endpoint**: `/api/catalog/categorias/`
- **Métodos**: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`
- **Extra**: `/api/catalog/categorias/papelera/` (GET), `/api/catalog/categorias/{id}/restaurar/` (POST)

### [Inventario] Movimientos
- **Endpoint**: `/api/movimientos/`
- **Métodos**: `GET`, `POST`
- **Restricción**: `PUT/PATCH/DELETE` no permitidos (Los movimientos son inmutables por integridad).
- **POST Input**:
  ```json
  {
    "tipo_movimiento": "ENTRADA",
    "producto_id": 1,
    "content_type": "chemicalproduct",
    "cantidad": 50,
    "ubicacion_destino": 5
  }
  ```

### [Auditoría] Logs
- **Endpoint**: `/api/auditoria/logs/`
- **Métodos**: `GET`
- **Restricción**: Solo lectura para administradores.
