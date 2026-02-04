# Arquitectura Backend (Refactorización 2026)

Esta guía describe la nueva arquitectura modular del backend, alineada con las mejores prácticas de Django y enfocada en inventario, geografía, instituciones, auditoría y compras.

## Objetivos del Refactor
- Claridad de modelos y responsabilidades mediante `ProductBase`.
- Tipos de productos especializados con stocks por tipo.
- Movimientos de inventario transaccionales con auditorías.
- Integración con ubicaciones (`geography`) y acueductos (`institucion`).
- Compatibilidad con nombres legacy vía proxies.

## Apps y Responsabilidades
- `inventario`: Productos, Stock, Movimientos, Auditoría, Fichas técnicas.
- `geography`: `Ubicacion` y entidades geográficas (State, Municipality, Parish).
- `institucion`: `OrganizacionCentral`, `Sucursal`, `Acueducto`.
- `compras`: `OrdenCompra` y flujos asociados a transferencias.
- `catalogo`: Catálogos maestros (Categoría, Marca, Unidades, Proveedores).

## Modelo Base de Productos
`ProductBase` (abstracto) define campos comunes: `nombre`, `sku`, `categoria`, `proveedor`, `unidad_medida`, precios y metadatos.

Implementaciones:
- `Pipe`: campos para material, diámetro, presión, longitud por unidad, `tipo_union`, `tipo_uso`.
- `PumpAndMotor`: identificación (marca/modelo/serie), potencia (HP/kW), eléctricos (voltaje/fases/frecuencia) y hidráulicos (caudal/altura/eficiencia).
- `Accessory`: tipo, subtipo, diámetros de entrada/salida, conexión, presión de trabajo, material.
- `ChemicalProduct`: seguridad (peligrosidad), concentración, presentación, fechas de caducidad.

Proxies Legacy (compatibilidad):
- `Categoria` → `CategoriaProducto`.
- `Tuberia` → `Pipe` (acepta `acueducto` y mapea a `Ubicacion`).
- `Equipo` → `PumpAndMotor`.
- `StockTuberia` → `StockPipe`.
- `StockEquipo` → `StockPumpAndMotor`.

## Stocks por Tipo
- `StockPipe`: calcula `metros_totales = cantidad * longitud_unitaria`.
- `StockPumpAndMotor`: cantidad de equipos y `estado_operativo`.
- `StockAccessory`: cantidad decimal por ubicación.
- `StockChemical`: cantidad por lote y `fecha_vencimiento`.

Reglas:
- `unique_together` sobre `(producto, ubicacion)` (y `lote` en químicos).
- Validadores para impedir cantidades negativas.

## Movimientos de Inventario
`MovimientoInventario` soporta tipos: ENTRADA, SALIDA, TRANSFER, AJUSTE.

- Relación genérica a producto (`content_type`, `object_id`).
- Reglas de stock:
  - ENTRADA (destino requerido): suma stock en destino.
  - SALIDA (origen requerido): resta stock; valida insuficiencia.
  - TRANSFER: resta en origen y suma en destino.
  - AJUSTE: suma en destino o resta en origen.

Auditoría (`InventoryAudit`): registra estado PENDING/SUCCESS/FAILED y contexto del movimiento.

Integración `compras` (TRANSFER): crea `OrdenCompra` con solicitante/aprobador; para `PumpAndMotor`, actualiza `FichaTecnicaMotor` según destino (Instalado vs En Almacén).

## Ubicaciones e Instituciones
- `Ubicacion` pertenece a `Acueducto` o `Parish` y tiene `tipo` ALMACEN/INSTALACION.
- Compatibilidad: kwargs legacy `acueducto` se mapean a `Ubicacion` por defecto (ALMACEN).

## Pruebas e Integración
- Pruebas en `inventario/tests/test_legacy.py` cubren:
  - Creación y validaciones de `Pipe`, `PumpAndMotor`, `Accessory`, `ChemicalProduct`.
  - Stocks: creación, negativos prohibidos, unicidad.
  - Movimientos: entrada/salida/transfer/ajuste; auditoría y efectos en ficha técnica.
- Ejecutar:
  - `python manage.py test inventario`
  - Con otras apps: `python manage.py test inventario geography institucion catalogo compras`

## Despliegue
- `docker-compose.yml` (dev) y `docker-compose.prod.yml` (prod).
- Nginx y `ssl/` para producción.
- `init-db.sh` para inicialización.

## Guías Relacionadas
- Ver [docs/GUIA_MODELOS_REFACTORIZADOS.md](docs/GUIA_MODELOS_REFACTORIZADOS.md).
- Ver [docs/GUIA_MIGRACION.md](docs/GUIA_MIGRACION.md).
- Ver [docs/PRUEBAS-E-INTEGRACION.md](docs/PRUEBAS-E-INTEGRACION.md).
