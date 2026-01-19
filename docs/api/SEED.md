# API Seed Rápido

Objetivo: crear datos mínimos para probar productos, stock y movimientos.

Requisitos: tener token en `$headers` (`Authorization: Token <TOKEN>`)

```powershell
# 1) Categorías
$catChem = @{ nombre='Productos Químicos'; codigo='QUI'; activo=$true; orden=1 } | ConvertTo-Json
Invoke-RestMethod -Headers $headers -Uri "http://localhost/api/catalog/categorias/" -Method Post -ContentType "application/json" -Body $catChem
$catPipe = @{ nombre='Tuberías'; codigo='TUB'; activo=$true; orden=2 } | ConvertTo-Json
Invoke-RestMethod -Headers $headers -Uri "http://localhost/api/catalog/categorias/" -Method Post -ContentType "application/json" -Body $catPipe

# 2) Unidad de medida
$u = @{ nombre='Unidad'; simbolo='u'; tipo='UNIDAD'; activo=$true } | ConvertTo-Json
Invoke-RestMethod -Headers $headers -Uri "http://localhost/api/units/" -Method Post -ContentType "application/json" -Body $u

# 3) Proveedor
$sup = @{ nombre='Proveedor Demo'; rif='J-12345678-9'; codigo='SUP001'; contacto_nombre='Juan'; telefono='0414-0000000'; email='demo@example.com'; direccion='Av. Principal'; activo=$true } | ConvertTo-Json
Invoke-RestMethod -Headers $headers -Uri "http://localhost/api/suppliers/" -Method Post -ContentType "application/json" -Body $sup

# 4) Ubicación (requiere acueducto existente)
# Si no tienes acueducto, crea uno en /api/acueductos/ con sucursal válida
$ub = @{ nombre='Almacén Central'; tipo='ALMACEN'; acueducto=1 } | ConvertTo-Json
Invoke-RestMethod -Headers $headers -Uri "http://localhost/api/geography/ubicaciones/" -Method Post -ContentType "application/json" -Body $ub

# 5) Producto: Tubería
$pipe = @{ nombre='Tubería PVC 110mm'; categoria=2; unidad_medida=1; proveedor=1; stock_minimo=50; stock_actual=0; precio_unitario=12.3; material='PVC'; diametro_nominal=110; unidad_diametro='MM'; presion_nominal='PN10'; tipo_union='EMBONE'; tipo_uso='AGUA_FRIA'; longitud_unitaria=6 } | ConvertTo-Json
Invoke-RestMethod -Headers $headers -Uri "http://localhost/api/pipes/" -Method Post -ContentType "application/json" -Body $pipe

# 6) Stock de Tubería
$stockPipe = @{ producto=1; ubicacion=1; cantidad=100 } | ConvertTo-Json
Invoke-RestMethod -Headers $headers -Uri "http://localhost/api/stock-pipes/" -Method Post -ContentType "application/json" -Body $stockPipe

# 7) Movimiento de Entrada
$movEntr = @{ tipo_movimiento='ENTRADA'; cantidad=50; product_type='pipe'; product_id=1; ubicacion_destino=1; razon='Ingreso lote' } | ConvertTo-Json
Invoke-RestMethod -Headers $headers -Uri "http://localhost/api/movimientos/" -Method Post -ContentType "application/json" -Body $movEntr
```

Tip: ajusta IDs según tus respuestas anteriores (`categoria`, `unidad_medida`, `proveedor`, `ubicacion`, `product_id`).
