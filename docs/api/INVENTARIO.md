# Inventario API

Base: /

Routers:
- Aux: /organizaciones/, /sucursales/, /units/, /suppliers/, /acueductos/, /users/
- Productos: /chemicals/, /pipes/, /pumps/, /accessories/
- Stock: /stock-chemicals/, /stock-pipes/, /stock-pumps/, /stock-accessories/
- Movimientos: /movimientos/
- Reportes: /reportes-v2/
- Mantenimiento: /fichas-tecnicas/, /mantenimientos/

Auth: Header `Authorization: Token <TOKEN>`

List examples:
```powershell
$h = @{ Authorization = "Token <TOKEN>" }
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/pipes/" -Method Get | ConvertTo-Json -Depth 3
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/chemicals/" -Method Get | ConvertTo-Json -Depth 3
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/accessories/" -Method Get | ConvertTo-Json -Depth 3
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/pumps/" -Method Get | ConvertTo-Json -Depth 3
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/movimientos/" -Method Get | ConvertTo-Json -Depth 3
```

Filters:
- `pipes`: categoria, activo, material, tipo_uso, presion_nominal, tipo_union, proveedor
- `chemicals`: categoria, activo, es_peligroso, nivel_peligrosidad, presentacion, proveedor
- `pumps`: categoria, activo, tipo_equipo, marca, fases, voltaje, proveedor
- `accessories`: categoria, activo, tipo_accesorio, subtipo, tipo_conexion, material, proveedor

Custom actions:
- `chemicals/stock_bajo/` GET
- `chemicals/peligrosos/` GET
- `chemicals/proximos_vencer/` GET
- `pipes/by_diameter/?diametro=110` GET
- `pumps/by_power_range/?min_hp=1&max_hp=10` GET
- `[product]/{id}/history/` GET for chemicals/pipes/pumps/accessories
- `movimientos/{id}/aprobar/` POST (admin)
- `movimientos/{id}/rechazar/` POST (admin)

Crear movimiento (entrada):
```powershell
$payload = @{ tipo_movimiento='ENTRADA'; cantidad=10; product_type='pipe'; product_id=1; ubicacion_destino=1; razon='Ingreso inicial' } | ConvertTo-Json
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/movimientos/" -Method Post -ContentType "application/json" -Body $payload
```

Aprobar/Rechazar movimiento (admin):
```powershell
# Aprobar
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/movimientos/1/aprobar/" -Method Post
# Rechazar
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/movimientos/1/rechazar/" -Method Post
```

Crear producto químico (mínimo):
```powershell
$payload = @{ nombre='Cloro'; descripcion='Hipoclorito'; categoria=1; unidad_medida=1; proveedor=1; stock_minimo=10; stock_actual=0; precio_unitario=5.5; es_peligroso=$true; nivel_peligrosidad='ALTA' } | ConvertTo-Json
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/chemicals/" -Method Post -ContentType "application/json" -Body $payload
```

Crear tubería (mínimo):
```powershell
$payload = @{ nombre='Tubería PVC 110mm'; categoria=2; unidad_medida=1; proveedor=1; stock_minimo=50; stock_actual=0; precio_unitario=12.3; material='PVC'; diametro_nominal=110; unidad_diametro='MM'; presion_nominal='PN10'; tipo_union='EMBONE'; tipo_uso='AGUA_FRIA'; longitud_unitaria=6 } | ConvertTo-Json
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/pipes/" -Method Post -ContentType "application/json" -Body $payload
```

Crear accesorio (mínimo):
```powershell
$payload = @{ nombre='Válvula de compuerta 2"'; categoria=4; unidad_medida=1; proveedor=1; stock_minimo=10; stock_actual=0; precio_unitario=25.0; tipo_accesorio='VALVULA'; tipo_conexion='ROSCA'; material='HIERRO' } | ConvertTo-Json
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/accessories/" -Method Post -ContentType "application/json" -Body $payload
```

Crear bomba/motor (mínimo):
```powershell
$payload = @{ nombre='Bomba Centrífuga 5HP'; categoria=3; unidad_medida=1; proveedor=1; stock_minimo=2; stock_actual=0; precio_unitario=500.0; tipo_equipo='BOMBA'; marca='KSB'; modelo='XYZ'; potencia_hp=5; voltaje=220; fases='TRIFASICO' } | ConvertTo-Json
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/pumps/" -Method Post -ContentType "application/json" -Body $payload
```

Crear stock de tubería:
```powershell
$payload = @{ producto=1; ubicacion=1; cantidad=100 } | ConvertTo-Json
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/stock-pipes/" -Method Post -ContentType "application/json" -Body $payload
```

Notas:
- `product_type`: one of `chemical|pipe|pump|accessory`
- `ubicacion_origen`/`ubicacion_destino` usan IDs de `geography.Ubicacion`
- Aprobaciones cambian stock si el movimiento está `PENDIENTE` y se `aprobar`.
 - Algunos campos usan choices (ej: `material`, `tipo_union`, `tipo_uso`, `fases`). Verifica valores válidos con la API o documentación interna.
