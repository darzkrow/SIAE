# Notificaciones API

Base: /notificaciones/

Endpoints:
- /notificaciones/: list/create/update/delete notifications
- /alertas/: list/create/update/delete alerts

Filters:
- notificaciones: `leida`, `tipo`
- alertas: `activo`, `acueducto`

Examples:
```powershell
$h = @{ Authorization = "Token <TOKEN>" }
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/notificaciones/notificaciones/" -Method Get | ConvertTo-Json -Depth 3
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/notificaciones/alertas/" -Method Get | ConvertTo-Json -Depth 3
```

Crear notificación:
```powershell
$payload = @{ titulo='Stock bajo'; mensaje='El stock de tuberías 110mm está bajo'; tipo='INFO'; leida=$false } | ConvertTo-Json
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/notificaciones/notificaciones/" -Method Post -ContentType "application/json" -Body $payload
```

Crear alerta:
```powershell
$payload = @{ titulo='Alerta crítica'; descripcion='Fuga en acueducto principal'; tipo='CRITICA'; activo=$true; acueducto=1 } | ConvertTo-Json
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/notificaciones/alertas/" -Method Post -ContentType "application/json" -Body $payload
```
