# Compras API

Base: /compras/

Endpoints:
- /ordenes/: list/create/update/delete purchase orders
- /items/: list/create items linked to an order

Actions:
- POST /ordenes/{id}/aprobar/: mark order as SOLICITADO, sets aprobador=user

Examples:
```powershell
$h = @{ Authorization = "Token <TOKEN>" }
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/compras/ordenes/" -Method Get | ConvertTo-Json -Depth 3

# Crear orden
$payload = @{ codigo='OC-0001'; solicitante=2; status='CREADA'; notas='Compra de prueba' } | ConvertTo-Json
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/compras/ordenes/" -Method Post -ContentType "application/json" -Body $payload

# Aprobar
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/compras/ordenes/1/aprobar/" -Method Post
```

Crear item de orden:
```powershell
$payload = @{ orden=1; producto_tipo='pipe'; producto_id=1; cantidad=50; precio_unitario=12.3 } | ConvertTo-Json
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/compras/items/" -Method Post -ContentType "application/json" -Body $payload
```

Filtrar órdenes por estado:
```powershell
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/compras/ordenes/?status=CREADA" -Method Get | ConvertTo-Json -Depth 3
```
