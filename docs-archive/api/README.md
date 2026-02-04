# API Overview

Base URL (Docker + Nginx): http://localhost/api/
Health: http://localhost/health

Authentication:
- Token auth: POST /accounts/api-token-auth/ with JSON {"username":"apiadmin","password":"Admin123!"}
- Use header: Authorization: Token <token>

Apps covered:
- Accounts: /accounts/
- Catalogo: /catalog/
- Inventario: /
- Compras: /compras/
- Auditoria: /auditoria/
- Notificaciones: /notificaciones/
- Geography: /geography/

Quick start (PowerShell):

```powershell
# Get token
$body = @{ username = 'apiadmin'; password = 'Admin123!' } | ConvertTo-Json
$tokenResp = Invoke-RestMethod -Method Post -Uri "http://localhost/api/accounts/api-token-auth/" -ContentType "application/json" -Body $body
$token = $tokenResp.token
$headers = @{ Authorization = "Token $token" }

# Example: list categories
Invoke-RestMethod -Headers $headers -Uri "http://localhost/api/catalog/categorias/" -Method Get | ConvertTo-Json -Depth 3
```

Notes:
- Admin-only endpoints (e.g., approving movements) require admin role.
- Pagination uses DRF defaults (`count`, `next`, `previous`, `results`).
- Filters via query params as documented per endpoint.
