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
