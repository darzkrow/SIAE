# Catalogo API

Base: /catalog/

Endpoints:
- /categorias/: list/create/update/delete categories
- /marcas/: list/create/update/delete brands

Filters:
- categorias: activo
- marcas: activo

Examples:
```powershell
$headers = @{ Authorization = "Token <TOKEN>" }
Invoke-RestMethod -Headers $headers -Uri "http://localhost/api/catalog/categorias/" -Method Get | ConvertTo-Json -Depth 3
Invoke-RestMethod -Headers $headers -Uri "http://localhost/api/catalog/marcas/" -Method Get | ConvertTo-Json -Depth 3
```

Create category:
```powershell
$payload = @{ nombre='Nueva'; codigo='NEW'; descripcion='Demo'; activo=$true; orden=99 } | ConvertTo-Json
Invoke-RestMethod -Headers $headers -Uri "http://localhost/api/catalog/categorias/" -Method Post -ContentType "application/json" -Body $payload
```
