# Diagrama de Flujo del Modelo de Inventario (SIAE)

Este documento describe el flujo de negocio del módulo de inventario para alinear el frontend con el backend. Incluye fases, modelos involucrados, endpoints y reglas clave.

## Visión General
- Objetivo: Gestionar productos por tipo (Químicos, Tuberías, Bombas/Motores, Accesorios), su stock por ubicación, movimientos, compras y alertas.
- Núcleo: `ProductBase` + subtipos; `Stock*` por ubicación; `MovimientoInventario` para entradas/salidas/transferencias/ajustes; auditoría y notificaciones.

## Modelos Clave
- Productos:
  - `ChemicalProduct`, `Pipe`, `PumpAndMotor`, `Accessory` extienden `ProductBase` en [backend/inventario/models.py](backend/inventario/models.py#L80-L140, backend/inventario/models.py#L450-L590).
  - `PumpAndMotor` fuerza categoría `BOM` y calcula kW en [backend/inventario/models.py](backend/inventario/models.py#L520-L590).
- Catálogo:
  - `CategoriaProducto`, `Marca` en [backend/catalogo/models.py](backend/catalogo/models.py#L1-L80).
- Stock por ubicación:
  - `StockChemical`, `StockPipe`, `StockPumpAndMotor`, `StockAccessory` en [backend/inventario/models.py](backend/inventario/models.py#L793-L825).
- Movimientos y Auditoría:
  - `MovimientoInventario` (ENTRADA/SALIDA/TRANSFERENCIA/AJUSTE), audit trail y aprobación en migración inicial [backend/inventario/migrations/0001_initial.py](backend/inventario/migrations/0001_initial.py#L68-L86, backend/inventario/migrations/0001_initial.py#L94-L103, backend/inventario/migrations/0001_initial.py#L135-L137).
- Notificaciones/Alertas:
  - Alertas de stock bajo y notificaciones en [backend/notificaciones/models.py](backend/notificaciones/models.py#L48-L62).

## Reglas de Negocio
- SKU: Se genera como `{categoria.codigo}-{TIPO}-{correlativo}` en `ProductBase.generate_sku()` [backend/inventario/models.py](backend/inventario/models.py#L176-L197).
- Categoría fija para bombas/motores: `PumpAndMotor.save()` asigna `CategoriaProducto(codigo='BOM')` [backend/inventario/models.py](backend/inventario/models.py#L528-L552).
- Unidad por defecto: Frontend selecciona automáticamente una unidad de tipo `UNIDAD` para Bombas/Motores.
- Stock mínimo y estado: `get_stock_status()` devuelve `AGOTADO/CRITICO/BAJO/NORMAL` [backend/inventario/models.py](backend/inventario/models.py#L200-L220).
- Alertas: Comando `check_stock_alerts` crea notificaciones si el stock < umbral [backend/inventario/management/commands/check_stock_alerts.py](backend/inventario/management/commands/check_stock_alerts.py#L12-L47).
- Auditoría y aprobación: Movimientos registran creador y aprobador (roles ADMIN/superuser).

## Endpoints Principales (DRF ViewSets)
- Productos:
  - Bombas/Motores: `/api/pumps/` en [backend/inventario/urls.py](backend/inventario/urls.py#L23) y [backend/inventario/views.py](backend/inventario/views.py#L259-L300).
  - Stock Bombas: `/api/stock-pumps/` en [backend/inventario/urls.py](backend/inventario/urls.py#L29) y [backend/inventario/views.py](backend/inventario/views.py#L412-L417).
  - Químicos/Tuberías/Accesorios: equivalentes (`/api/chemicals/`, `/api/pipes/`, `/api/accessories/`) según configuración del proyecto.
- Catálogo:
  - Categorías: `/api/catalog/categorias/` consumido por frontend [frontend/src/services/inventory.service.js](frontend/src/services/inventory.service.js#L40).
  - Marcas: `/api/catalog/marcas/` (seed en [backend/catalogo/fixtures/marcas_populares.json](backend/catalogo/fixtures/marcas_populares.json)).
- Compras:
  - Órdenes: `/api/compras/ordenes/` (flujo de ingreso de stock por recepción).
- Notificaciones:
  - `/api/notificaciones/`, `/api/alertas/` en [backend/notificaciones/urls.py](backend/notificaciones/urls.py#L6-L7).

## Flujo de Negocio (Texto)
1. Configuración Inicial
   - Crear categorías (`QUI`, `TUB`, `BOM`, `ACC`), unidades de medida y proveedores.
   - Sembrar marcas para `PumpAndMotor`.
2. Registro de Producto
   - Frontend muestra formularios por tipo: Químico, Tubería, Bomba/Motor, Accesorio.
   - `PumpForm`: fija categoría a `BOM`, selecciona unidad tipo `UNIDAD`, exige campos: tipo_equipo, marca, modelo, número_serie, potencia_hp, voltaje, fases.
   - Backend valida, genera SKU y guarda.
3. Asignación de Stock
   - Crear `Stock*` por `Ubicacion` (planta, almacén, instalación).
   - Estado operativo aplica para `StockPumpAndMotor`.
4. Movimientos de Inventario
   - Tipos: ENTRADA (incrementa stock en destino), SALIDA (decrementa stock en origen), TRANSFERENCIA (origen→destino), AJUSTE (corrección).
   - Requieren aprobación (según rol). Se audita cada movimiento.
5. Compras y Recepciones
   - Órdenes de compra generan ENTRADA al recibir; vinculan movimiento y actualizan stock.
6. Alertas y Notificaciones
   - Cron/Comando revisa stock bajo por umbral; crea alertas y envía correo si configurado.
7. Reportes/Consultas
   - Listados por categoría, rango de potencia, estado de stock y ubicaciones.

## Diagrama (Mermaid)
```mermaid
flowchart TD
  A[Configuración Inicial<br/>Categorías, Unidades, Proveedores, Marcas] --> B[Registro de Producto<br/>ProductBase + Subtipo]
  B --> C[Producto guardado (SKU autogenerado)]
  C --> D[Asignación de Stock<br/>Stock* por Ubicación]
  D --> E{Movimiento}
  E -->|ENTRADA| F[Incrementa Stock Destino]
  E -->|SALIDA| G[Decrementa Stock Origen]
  E -->|TRANSFERENCIA| H[Stock Origen→Destino]
  E -->|AJUSTE| I[Corrige Stock]
  F --> J[Auditoría & Aprobación]
  G --> J
  H --> J
  I --> J
  J --> K[Alertas de Stock Bajo]
  K --> L[Notificaciones]
  C --> M[Consultas/Reportes]
  subgraph Productos
    C1[ChemicalProduct]
    C2[Pipe]
    C3[PumpAndMotor\n(categoría BOM fija)]
    C4[Accessory]
  end
  B --> C1
  B --> C2
  B --> C3
  B --> C4
```

## Mapeo Frontend ↔ Backend (Puntos a Alinear)
- Formularios por tipo: Asegurar campos requeridos coinciden con los modelos (p.ej. `PumpAndMotor`).
- Categoría fija en bombas: Ya bloqueada en [frontend/src/components/forms/PumpForm.jsx](frontend/src/components/forms/PumpForm.jsx) y forzada en backend.
- Respuesta paginada vs arreglo: Normalizada en páginas (Catálogo, Geografía, Auditoría, Notificaciones).
- Stock y movimientos: UI debe persistir tipo de movimiento y ubicaciones origen/destino acorde a backend.

## Acceso y Seguridad
- Admin Django: HTTP en `/admin/` (Nginx), acceso restringido a redes locales en [nginx/nginx.conf](nginx/nginx.conf#L33-L49).
- API: `/api/*` proxied a backend; auditoría y permisos por rol.

## Próximos pasos sugeridos
- Ajustar formularios de Movimientos en el frontend para reflejar los cuatro tipos y aprobación.
- Añadir filtros de marcas y potencia para Bombas.
- Parametrizar `BOM` vía configuración si se desea flexibilidad.
