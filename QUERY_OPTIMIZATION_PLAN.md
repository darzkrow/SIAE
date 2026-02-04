# 🚀 Plan de Optimización de Queries - Fase 7

## 📊 Análisis Inicial

### ViewSets con Optimización Existente ✅
1. **geography/views.py**
   - `Municipality` → `select_related('state')`
   - `Parish` → `select_related('municipality__state')`
   - `Ubicacion` → `select_related('parish', 'acueducto')`

2. **inventario/views.py**
   - `Sucursal` → `select_related('organizacion_central')`
   - `User` → `select_related('sucursal')`
   - `ChemicalProduct` → `select_related('categoria', 'unidad_medida', 'proveedor')`
   - `Pipe` → `select_related('categoria', 'unidad_medida', 'proveedor')`
   - `PumpAndMotor` → `select_related('categoria', 'marca', 'proveedor')`
   - `Accessory` → `select_related('categoria', 'unidad_medida', 'proveedor')`
   - `StockChemical` → `select_related('producto', 'ubicacion', 'acueducto')`
   - `StockPipe` → `select_related('producto', 'ubicacion', 'acueducto')`
   - `StockPumpAndMotor` → `select_related('producto', 'ubicacion', 'acueducto')`
   - `StockAccessory` → `select_related('producto', 'ubicacion', 'acueducto')`

3. **institucion/views.py**
   - `Empresa` → `prefetch_related('subsidiarias', 'vicepresidencias')`
   - `Vicepresidencia` → `select_related('empresa', 'responsable')` + `prefetch_related('unidades_organizacionales')`

### ViewSets SIN Optimización (N+1 Queries) ❌

#### Alta Prioridad (Relaciones ForeignKey)
1. **institucion/views.py**
   - `UnidadOrganizacional` → Necesita `select_related('vicepresidencia', 'responsable')`
   - `AlmacenRegional` → Necesita `select_related('unidad_organizacional', 'manager')`
   - `Sucursal` → Necesita `select_related('organizacion_central')`
   - `Acueducto` → Necesita `select_related('sucursal')`
   - `ActivoInventario` → Necesita `select_related('tipo_activo', 'almacen_actual', 'unidad_organizacional')`
   - `SolicitudTraslado` → Necesita `select_related('activo', 'almacen_origen', 'almacen_destino', 'solicitante')`
   - `HistorialMovimientoActivo` → Necesita `select_related('activo', 'almacen_origen', 'almacen_destino', 'usuario')`
   - `MigracionOrganizacional` → Necesita `select_related('empresa', 'vicepresidencia', 'unidad_organizacional', 'migrado_por')`

2. **inventario/views.py**
   - `OrganizacionCentral` → Necesita `prefetch_related('sucursales')`
   - `Acueducto` → Necesita `select_related('sucursal')`
   - `FichaTecnicaMotor` → Necesita optimización
   - `RegistroMantenimiento` → Necesita optimización

3. **catalogo/views.py**
   - `CategoriaProducto` → Sin relaciones complejas (OK)
   - `Marca` → Sin relaciones complejas (OK)

4. **compras/views.py**
   - `OrdenCompra` → Necesita `select_related('solicitante', 'movimiento')` + `prefetch_related('items')`
   - `ItemOrden` → Necesita `select_related('orden', 'content_type')`

5. **auditoria/views.py**
   - `AuditLog` → Necesita `select_related('user', 'content_type')`

6. **notificaciones/views.py**
   - `Notificacion` → Necesita `select_related('user')`
   - `Alerta` → Necesita optimización

#### Media Prioridad (Relaciones ManyToMany)
- `ChemicalProduct.tags` → Necesita `prefetch_related('tags')`
- `Pipe.tags` → Necesita `prefetch_related('tags')`
- Otros productos con tags

## 🎯 Estrategia de Optimización

### 1. Reglas de Optimización
- **ForeignKey** → Usar `select_related()`
- **ManyToMany** → Usar `prefetch_related()`
- **Reverse ForeignKey** → Usar `prefetch_related()`
- **Nested relations** → Usar `Prefetch()` objects

### 2. Priorización
1. **Alta:** ViewSets más usados (institucion, inventario, compras)
2. **Media:** ViewSets de soporte (auditoria, notificaciones)
3. **Baja:** ViewSets administrativos

### 3. Patrón de Implementación
```python
def get_queryset(self):
    return super().get_queryset().select_related(
        'fk_field1',
        'fk_field2__nested_fk'
    ).prefetch_related(
        'm2m_field1',
        'reverse_fk_field'
    )
```

## 📝 Archivos a Modificar

1. `backend/institucion/views.py` (9 viewsets)
2. `backend/inventario/views.py` (4 viewsets)
3. `backend/compras/views.py` (2 viewsets)
4. `backend/auditoria/views.py` (1 viewset)
5. `backend/notificaciones/views.py` (2 viewsets)

**Total:** ~18 viewsets a optimizar

## 📈 Impacto Esperado

### Antes (N+1 Queries)
```
List 100 ActivoInventario:
- 1 query para ActivoInventario
- 100 queries para tipo_activo
- 100 queries para almacen_actual
- 100 queries para unidad_organizacional
= 301 queries total
```

### Después (Optimizado)
```
List 100 ActivoInventario:
- 1 query para ActivoInventario
- 1 query para tipo_activo (JOIN)
- 1 query para almacen_actual (JOIN)
- 1 query para unidad_organizacional (JOIN)
= 4 queries total
```

**Reducción:** 301 → 4 queries (98.7% menos queries)  
**Performance:** 50-80% más rápido en endpoints de listado

## ✅ Verificación

Después de optimizar, verificar con:
```python
from django.db import connection
from django.test.utils import override_settings

@override_settings(DEBUG=True)
def test_query_count():
    connection.queries = []
    response = client.get('/api/activos/')
    print(f"Queries: {len(connection.queries)}")
    for q in connection.queries:
        print(q['sql'])
```

## 🚀 Implementación

Proceder en orden:
1. institucion/views.py (mayor impacto)
2. inventario/views.py
3. compras/views.py
4. auditoria/views.py
5. notificaciones/views.py
