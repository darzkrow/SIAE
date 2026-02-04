# Despliegue en Producción (Docker)

Este documento resume los pasos para construir y ejecutar la aplicación en producción usando Docker y `docker-compose`.

Requisitos:
- Docker y Docker Compose instalados en el servidor.
- Variables de entorno seguras: `DJANGO_SECRET_KEY`, `DB_*` (si no se usan defaults), `ALLOWED_HOSTS`.

1) Generar una `DJANGO_SECRET_KEY` (en el servidor):

```bash
python - <<'PY'
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
PY
```

2) Crear un archivo `.env` con al menos las variables:

```env
DJANGO_SECRET_KEY=tu_secreto_generado_aqui
DB_NAME=gsih_inventario
DB_USER=gsih_user
DB_PASSWORD=strongpassword
ALLOWED_HOSTS=example.com,www.example.com
VITE_API_URL=https://api.example.com
```

3) Construir y levantar los servicios (modo producción):

```bash
docker compose -f docker-compose.prod.yml --env-file .env up --build -d
```

4) El contenedor del backend ejecuta automáticamente migraciones y `collectstatic` en el `entrypoint`. Ver logs si hay errores:

```bash
docker compose -f docker-compose.prod.yml logs -f backend
```

5) Verificación básica:
- Acceder a `http://<HOST>` y comprobar que la app carga.
- Revisar que `nginx` sirve archivos estáticos montados desde el volumen `static_volume`.

Notas y recomendaciones:
- Usar un reverse proxy (nginx ya incluido) y gestionar certificados TLS (Let's Encrypt) para `443`.
- Monitorizar logs y configurar un sistema de alertas.
- Añadir backups periódicos del volumen de Postgres.
- Ajustar número de workers de Gunicorn según la CPU/recursos del servidor.

## SSL/TLS con Nginx (Let’s Encrypt)

1) Instala Certbot en el host y obtiene certificados para tu dominio.
2) Configura `nginx/nginx.conf` para servir HTTPS y redirigir HTTP → HTTPS.

Ejemplo de servidor Nginx:
```
server {
	listen 80;
	server_name example.com www.example.com;
	return 301 https://$host$request_uri;
}

server {
	listen 443 ssl;
	server_name example.com www.example.com;

	ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
	ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

	location /static/ {
		alias /usr/share/nginx/html/static/;
	}

	location / {
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;
		proxy_pass http://backend:8000;
	}
}
```

## Health Checks y recursos

- Gunicorn: ajusta workers a `2 * CPU + 1`.
- Configura `readiness/liveness` revisando el endpoint raíz o `/health/` si existe.
- Asegura `collectstatic` y migraciones en entrypoint.
- Monitorea con `docker compose logs -f backend` y `docker compose logs -f nginx`.

## Backups y base de datos

- Programa backups del volumen de Postgres (`pg_dump`).
- Considera réplicas si el entorno lo requiere.

## Frontend en producción

- Build estático con `npm run build`.
- Sirve assets con Nginx (bloque `/static/` y carpeta de `build` si aplica).
