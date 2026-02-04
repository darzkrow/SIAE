# Configuración de Red y Seguridad - SIAE

## Configuración Implementada

### Puertos
- **Backend (Django/Daphne)**: Puerto 8080 (interno: 8000)
- **Frontend (React/Vite)**: Puerto 8181 (interno: 5173)
- **Nginx (Reverse Proxy)**: Puerto 80
- **PostgreSQL**: Puerto 5432 (solo accesible internamente)

### Dominio
- **Dominio de Producción**: `sigei.hidroven.gob.ve`
- El frontend y backend están configurados para usar este dominio

### Restricciones de Seguridad

#### 1. Panel de Administración (`/admin/`)
**Acceso restringido SOLO a red local**

Rangos de IP permitidos:
- `192.168.0.0/16` - Redes privadas clase C
- `10.0.0.0/8` - Redes privadas clase A
- `172.16.0.0/12` - Redes privadas clase B
- `127.0.0.1` - Localhost

**Cualquier acceso desde fuera de estas redes será bloqueado con error 403 Forbidden**

#### 2. Documentación API (`/api/docs/`, `/api/redoc/`, `/api/schema/`)
**Acceso restringido SOLO a red local**

Mismos rangos de IP que el panel de administración.

#### 3. API REST (`/api/`)
**Acceso público** - Disponible desde cualquier origen
- Protegido por autenticación JWT/Token
- CORS configurado para el dominio de producción

### CORS (Cross-Origin Resource Sharing)
Orígenes permitidos:
- `http://sigei.hidroven.gob.ve`
- `http://localhost:8181` (desarrollo)
- `http://127.0.0.1:8181` (desarrollo)

### Configuración de Nginx

El archivo `nginx/nginx.conf` implementa:
1. **Proxy reverso** para el backend Django
2. **Servicio de archivos estáticos** del frontend React
3. **Restricciones de IP** para rutas sensibles
4. **Soporte para WebSockets** en `/ws/`
5. **Servicio de archivos estáticos Django** en `/static/` y `/media/`

### Flujo de Conexión

```
Cliente → Nginx (Puerto 80)
    ├─ / → Frontend React (archivos estáticos)
    ├─ /api/ → Backend Django (Puerto 8000 interno)
    ├─ /admin/ → Backend Django (SOLO RED LOCAL)
    ├─ /api/docs/ → Swagger UI (SOLO RED LOCAL)
    ├─ /static/ → Archivos estáticos Django
    ├─ /media/ → Archivos multimedia Django
    └─ /ws/ → WebSockets (Django Channels)
```

### Verificación de Configuración

Para verificar que las restricciones funcionan correctamente:

1. **Desde red local** (debería funcionar):
   ```bash
   curl http://sigei.hidroven.gob.ve/admin/
   curl http://sigei.hidroven.gob.ve/api/docs/
   ```

2. **Desde red externa** (debería retornar 403):
   ```bash
   curl http://sigei.hidroven.gob.ve/admin/
   # Respuesta esperada: 403 Forbidden
   ```

3. **API pública** (debería funcionar desde cualquier lugar):
   ```bash
   curl http://sigei.hidroven.gob.ve/api/
   ```

### Notas de Seguridad

1. **Cambiar contraseñas por defecto** en `.env`:
   - `SECRET_KEY`
   - `DB_PASSWORD`
   - `POSTGRES_PASSWORD`

2. **Configurar DEBUG=False** en producción

3. **Ajustar rangos de IP** según la red local real de la organización

4. **Configurar HTTPS** para producción (certificado SSL/TLS)

5. **Implementar rate limiting** adicional si es necesario
