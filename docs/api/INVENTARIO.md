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

Notas:
- `product_type`: one of `chemical|pipe|pump|accessory`
- `ubicacion_origen`/`ubicacion_destino` usan IDs de `geography.Ubicacion`
- Aprobaciones cambian stock si el movimiento está `PENDIENTE` y se `aprobar`.
