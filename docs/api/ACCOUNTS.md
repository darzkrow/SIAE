# Accounts API

Base: /accounts/

Endpoints:
- POST /api-token-auth/: obtain token
- GET /me/: authenticated user profile
- /users/: CRUD of users (admin only)

Examples (PowerShell):
```powershell
# Token
$body = @{ username = 'apiadmin'; password = 'Admin123!' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://localhost/api/accounts/api-token-auth/" -ContentType "application/json" -Body $body

# Profile
$headers = @{ Authorization = "Token <TOKEN>" }
Invoke-RestMethod -Headers $headers -Uri "http://localhost/api/accounts/me/" -Method Get | ConvertTo-Json -Depth 3

# List users (admin)
Invoke-RestMethod -Headers $headers -Uri "http://localhost/api/accounts/users/" -Method Get | ConvertTo-Json -Depth 3
```

Create user (admin):
```powershell
$payload = @{ username='jdoe'; email='jdoe@example.com'; password='Passw0rd!'; role='OPERADOR' } | ConvertTo-Json
Invoke-RestMethod -Headers $headers -Uri "http://localhost/api/accounts/users/" -Method Post -ContentType "application/json" -Body $payload
```
