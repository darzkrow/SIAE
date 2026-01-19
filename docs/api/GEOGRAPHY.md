# Geography API

Base: /geography/

Endpoints:
- /states/, /municipalities/, /parishes/: list divisions
- /ubicaciones/: CRUD of `Ubicacion` used in stock/movements (requires IDs in inventario)

Examples:
```powershell
$h = @{ Authorization = "Token <TOKEN>" }
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/geography/states/" -Method Get | ConvertTo-Json -Depth 3
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/geography/ubicaciones/" -Method Get | ConvertTo-Json -Depth 3
```

Create `Ubicacion`:
```powershell
$payload = @{ nombre='Almacén Central'; tipo='ALMACEN'; acueducto=1 } | ConvertTo-Json
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/geography/ubicaciones/" -Method Post -ContentType "application/json" -Body $payload
```
