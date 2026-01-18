# Solución de Problemas CORS

## Problema Identificado
El frontend estaba intentando conectarse directamente al backend en `http://10.10.50.26:8000`, lo que causaba errores CORS porque:
1. El navegador bloqueaba las peticiones cross-origin
2. No se estaba usando el proxy de Nginx correctamente

## Solución Implementada

### 1. Configuración del Frontend (`frontend/src/config.js`)
```javascript
// Usar rutas relativas en producción (a través de Nginx)
const isDevelopment = import.meta.env.DEV;
export const API_BASE_URL = isDevelopment 
  ? (import.meta.env.VITE_API_URL || 'http://localhost:8080')
  : ''; // Ruta relativa - usa el mismo dominio que el frontend
```

**Beneficios:**
- En producción, todas las peticiones van a `/api/...` (mismo dominio)
- Nginx hace proxy pass al backend internamente
- No hay problemas de CORS porque no es cross-origin

### 2. Configuración CORS del Backend (`backend/config/settings.py`)
```python
CORS_ALLOW_ALL_ORIGINS = env.bool('CORS_ALLOW_ALL_ORIGINS', default=DEBUG)

if not CORS_ALLOW_ALL_ORIGINS:
    # Producción - orígenes específicos
    CORS_ALLOWED_ORIGINS = [
        'http://sigei.hidroven.gob.ve',
        'https://sigei.hidroven.gob.ve',
        'http://localhost',
        'http://localhost:80',
        'http://127.0.0.1',
    ]
else:
    # Desarrollo - permitir múltiples orígenes
    CORS_ALLOWED_ORIGINS = [
        'http://localhost:5173',
        'http://localhost:8181',
        'http://localhost:80',
        'http://localhost',
        'http://127.0.0.1',
        'http://10.10.50.26',
        'http://sigei.hidroven.gob.ve',
        # ... más variaciones
    ]
```

### 3. Variables de Entorno (`.env`)
```env
CORS_ALLOW_ALL_ORIGINS=True  # Solo para desarrollo
```

## Flujo de Peticiones Correcto

### Desarrollo (con CORS_ALLOW_ALL_ORIGINS=True)
```
Frontend (localhost:8181) 
    → Backend directo (localhost:8080/api/...)
    → CORS permitido por configuración
```

### Producción (CORS_ALLOW_ALL_ORIGINS=False)
```
Browser (sigei.hidroven.gob.ve)
    → Nginx (puerto 80)
        ├─ / → Frontend estático
        └─ /api/ → Proxy Pass → Backend (puerto 8000 interno)
```

**No hay CORS** porque todo viene del mismo origen (sigei.hidroven.gob.ve)

## Verificación

### Prueba 1: Verificar CORS Headers
```bash
curl -I -H "Origin: http://localhost" http://localhost:8080/api/
# Debería incluir: Access-Control-Allow-Origin: *
```

### Prueba 2: Verificar Proxy de Nginx
```bash
curl http://localhost/api/
# Debería responder correctamente sin errores CORS
```

### Prueba 3: Login desde el Frontend
1. Abrir `http://localhost/` en el navegador
2. Intentar login
3. Verificar en DevTools Network que la petición va a `/api/accounts/api-token-auth/`
4. No debería haber errores CORS

## Configuración para Producción

Cuando se despliegue en producción:

1. **Cambiar `.env`:**
```env
DEBUG=False
CORS_ALLOW_ALL_ORIGINS=False
```

2. **Configurar DNS:**
```
sigei.hidroven.gob.ve → IP del servidor
```

3. **El frontend automáticamente usará rutas relativas** (porque `isDevelopment` será `false`)

4. **Nginx manejará todo el tráfico:**
   - Frontend: `http://sigei.hidroven.gob.ve/`
   - API: `http://sigei.hidroven.gob.ve/api/`
   - Admin: `http://sigei.hidroven.gob.ve/admin/` (solo red local)

## Notas Importantes

⚠️ **NUNCA usar `CORS_ALLOW_ALL_ORIGINS=True` en producción**
- Es un riesgo de seguridad
- Solo para desarrollo local

✅ **En producción, usar el proxy de Nginx**
- Evita problemas de CORS completamente
- Mejor rendimiento
- Más seguro

✅ **Configurar HTTPS en producción**
- Obtener certificado SSL/TLS
- Actualizar Nginx para escuchar en puerto 443
- Forzar redirección HTTP → HTTPS
