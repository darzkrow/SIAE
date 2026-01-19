# Auditoria API

Base: /auditoria/

Endpoints:
- /logs/: read-only audit logs

Notes:
- Requires admin permissions.
- Filters: search `object_repr`, `user__username`, `action`; ordering `timestamp`.

Examples:
```powershell
$h = @{ Authorization = "Token <TOKEN>" }
Invoke-RestMethod -Headers $h -Uri "http://localhost/api/auditoria/logs/" -Method Get | ConvertTo-Json -Depth 3
```
