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

Si quieres, puedo:
- Ajustar `nginx.conf` para Let’s Encrypt + redirección HTTPS.
- Añadir un `Dockerfile` optimizado para producción del `frontend` que genere los assets estáticos y los copie donde nginx los sirva.
