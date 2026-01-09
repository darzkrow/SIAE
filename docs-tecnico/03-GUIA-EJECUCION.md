# 🚀 GUÍA DE EJECUCIÓN - PROYECTO GSIH

## Requisitos Previos

- Python 3.11+
- Node.js 18+
- pip (gestor de paquetes Python)
- npm (gestor de paquetes Node)

## Instalación y Configuración

### 1. Backend (Django)

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Realizar migraciones
python manage.py makemigrations
python manage.py migrate

# Crear datos de prueba (seed)
python manage.py seed_inventario

# Crear superusuario (opcional)
python manage.py createsuperuser
```

### 2. Frontend (React + Vite)

```bash
# Navegar a la carpeta frontend
cd frontend

# Instalar dependencias
npm install

# Volver a la raíz
cd ..
```

## Ejecución

### Opción 1: Ejecución Manual (Desarrollo)

**Terminal 1 - Backend:**
```bash
# Activar entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Ejecutar servidor Django
python manage.py runserver
```

El backend estará disponible en: `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

El frontend estará disponible en: `http://localhost:5173`

### Opción 2: Docker Compose (Recomendado)

```bash
# Construir y ejecutar contenedores
docker-compose up --build

# En otra terminal, ejecutar migraciones y seed
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py seed_inventario
```

Backend: `http://localhost:8000`
Frontend: `http://localhost:5173`

## Credenciales de Prueba

**Usuario**: admin
**Contraseña**: admin

## Endpoints Principales

### Autenticación
- `POST /api/accounts/api-token-auth/` - Login
- `GET /api/accounts/me/` - Perfil del usuario

### Inventario
- `GET /api/tuberias/` - Lista de tuberías
- `GET /api/equipos/` - Lista de equipos
- `GET /api/stock-tuberias/` - Stock de tuberías
- `GET /api/stock-equipos/` - Stock de equipos

### Movimientos
- `GET /api/movimientos/` - Lista de movimientos
- `POST /api/movimientos/` - Crear movimiento
- `GET /api/audits/` - Auditoría de movimientos

### Reportes
- `GET /api/reportes/dashboard_stats/` - Estadísticas del dashboard
- `GET /api/reportes/stock_por_sucursal/` - Stock por sucursal
- `GET /api/reportes/alertas_stock_bajo/` - Alertas de stock bajo
- `GET /api/reportes/movimientos_recientes/` - Movimientos recientes

## Pruebas de API

### Con curl

```bash
# Login
curl -X POST http://localhost:8000/api/accounts/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'

# Usar token en requests
TOKEN="tu_token_aqui"
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/reportes/dashboard_stats/
```

### Con script Python

```bash
python test_api_endpoints.py
```

## Configuración de Email (Opcional)

Para habilitar notificaciones por email, configurar variables de entorno:

```bash
# En .env o en docker-compose.yml
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=noreply@gsih.com
STOCK_ALERT_EMAILS=admin@empresa.com,ops@empresa.com
```

Luego ejecutar el comando de alertas:

```bash
python manage.py check_stock_alerts
```

## Estructura del Proyecto

```
GSIH/
├── backend/
│   ├── accounts/          # Autenticación y usuarios
│   ├── inventario/        # Modelos y lógica de inventario
│   ├── config/            # Configuración de Django
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   ├── pages/         # Páginas/vistas
│   │   ├── context/       # Context API
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── docs/                  # Documentación
└── docker-compose.yml
```

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'django'"

```bash
# Asegúrate de que el entorno virtual está activado
# Reinstala las dependencias
pip install -r requirements.txt
```

### Error: "Port 8000 already in use"

```bash
# Cambiar puerto
python manage.py runserver 8001
```

### Error: "Port 5173 already in use"

```bash
# En frontend, cambiar puerto
npm run dev -- --port 5174
```

### Error: "CORS error"

Asegúrate de que `CORS_ALLOW_ALL_ORIGINS = True` en `config/settings.py` (solo para desarrollo)

### Error: "Token authentication failed"

1. Verifica que el token sea válido
2. Asegúrate de que el header sea: `Authorization: Token <token>`
3. Intenta hacer login nuevamente

## Comandos Útiles

```bash
# Backend
python manage.py shell                    # Shell interactivo de Django
python manage.py admin                    # Panel de administración
python manage.py makemigrations           # Crear migraciones
python manage.py migrate                  # Aplicar migraciones
python manage.py seed_inventario          # Cargar datos de prueba
python manage.py check_stock_alerts       # Verificar alertas de stock

# Frontend
npm run dev                               # Servidor de desarrollo
npm run build                             # Compilar para producción
npm run preview                           # Vista previa de producción
npm run lint                              # Verificar código

# Docker
docker-compose up                         # Iniciar contenedores
docker-compose down                       # Detener contenedores
docker-compose logs -f                    # Ver logs en tiempo real
```

## Acceso a Servicios

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/
- **Admin Django**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/ (si está configurado)

## Próximos Pasos

1. Explorar el dashboard
2. Crear movimientos de inventario
3. Revisar stock por sucursal
4. Configurar alertas de stock bajo
5. Generar reportes