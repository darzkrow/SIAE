# 🚀 Sistema de Gestión de Inventario de Activos Hidrológicos (GSIH)

Sistema de inventario integral para la gestión de tuberías, equipos y stock en acueductos, desarrollado con Django REST Framework y React.

## 📊 Estado del Proyecto

**Versión**: 1.0.0  
**Estado**: ✅ Production Ready (100%)  
**Backend**: Django REST Framework  
**Frontend**: React + Vite + TailwindCSS  
**Base de Datos**: PostgreSQL  

---

## ✨ Características Principales

### 🔐 Seguridad
- ✅ Autenticación con JWT tokens
- ✅ Permisos basados en roles (ADMIN/OPERADOR)
- ✅ CORS configurado de forma segura
- ✅ Rate limiting implementado
- ✅ Validación de entrada en todos los endpoints

### 📦 Gestión de Inventario
- ✅ CRUD completo de tuberías y equipos
- ✅ Control de stock en tiempo real
- ✅ Movimientos: ENTRADA, SALIDA, TRANSFERENCIA, AJUSTE
- ✅ Validación de stock disponible
- ✅ Auditoría completa de cambios

### 🔔 Alertas y Notificaciones
- ✅ Sistema de alertas de stock bajo
- ✅ Notificaciones por email configurables
- ✅ Panel de notificaciones en tiempo real

### 📊 Reportes y Estadísticas
- ✅ Dashboard con métricas en tiempo real
- ✅ Reportes de stock por sucursal
- ✅ Búsqueda avanzada con múltiples filtros
- ✅ Exportación de datos
- ✅ Gráficos y visualizaciones

### 📖 Documentación API
- ✅ Swagger/OpenAPI interactivo
- ✅ Documentación automática de endpoints
- ✅ Ejemplos de requests/responses

---

## 🚀 Inicio Rápido

### Prerequisitos

- Python 3.9+
- Node.js 18+
- PostgreSQL 13+ (o usar SQLite para desarrollo)
- Docker y Docker Compose (opcional)

### Instalación con Docker (Recomendado)

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd SISTEMA\ DE\ INVENTARIOS\ DE\ ACTIVOS\ EXTRATEGICOS

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 3. Ejecutar con Docker Compose
docker-compose up --build

# 4. Crear superusuario (en otra terminal)
docker-compose exec backend python manage.py createsuperuser

# Acceder a:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - Admin: http://localhost:8000/admin
# - API Docs: http://localhost:8000/api/docs/
```

### Instalación Local

#### Backend

```bash
# 1. Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 4. Ejecutar migraciones
python manage.py migrate

# 5. Crear superusuario
python manage.py createsuperuser

# 6. Ejecutar servidor de desarrollo
python manage.py runserver
```

#### Frontend

```bash
# 1. Ir al directorio frontend
cd frontend

# 2. Instalar dependencias
npm install

# 3. Ejecutar servidor de desarrollo
npm run dev
```

---

## 🔧 Configuración

### Variables de Entorno

Ver archivo `.env.example` para todas las variables disponibles.

**Mínimas requeridas para producción:**

```bash
# Django
DJANGO_SECRET_KEY=tu-secret-key-segura
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com

# Database (PostgreSQL)
DATABASE_URL=postgresql://usuario:password@localhost:5432/nombre_db

# CORS
CORS_ALLOWED_ORIGINS=https://tudominio.com,https://www.tudominio.com
```

### Base de Datos

#### PostgreSQL (Producción)

```bash
# Configurar DATABASE_URL
export DATABASE_URL=postgresql://usuario:password@localhost:5432/nombre_db

# O en .env
DATABASE_URL=postgresql://usuario:password@localhost:5432/nombre_db
```

#### SQLite (Desarrollo)

Por defecto usa SQLite si no se configura `DATABASE_URL`.

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests con coverage
pytest

# Tests específicos
pytest inventario/tests/test_models.py
pytest inventario/tests/test_api.py

# Con coverage report
pytest --cov=inventario --cov=accounts --cov-report=html

# Ver reporte
# Windows:
start htmlcov/index.html
# Linux/Mac:
open htmlcov/index.html
```

### Coverage Objetivo

- **Mínimo**: 70%
- **Objetivo**: 80%
- **Áreas críticas**: 95%

---

## 📚 Documentación API

### Swagger UI (Interactivo)

Acceder a: `http://localhost:8000/api/docs/`

### Endpoints Principales

#### Autenticación
```
POST /api/accounts/login/
POST /api/accounts/logout/
GET  /api/accounts/me/
```

#### Inventario
```
GET/POST /api/tuberias/
GET/POST /api/equipos/
GET/POST /api/stock-tuberias/
GET/POST /api/stock-equipos/
```

#### Movimientos
```
GET/POST /api/movimientos/
GET      /api/audits/
```

#### Reportes
```
GET /api/reportes/dashboard_stats/
GET /api/reportes/stock_por_sucursal/
GET /api/reportes/stock_search/
```

---

## 🏗️ Estructura del Proyecto

```
SISTEMA DE INVENTARIOS DE ACTIVOS EXTRATEGICOS/
├── config/                 # Configuración Django
│   ├── settings.py        # Settings principal
│   ├── urls.py            # URLs globales
│   └── wsgi.py
├── inventario/            # App principal
│   ├── models.py          # Modelos de datos
│   ├── views.py           # Views API
│   ├── serializers.py     # Serializers DRF
│   ├── permissions.py     # Permisos custom
│   ├── tests/             # Tests unitarios
│   │   ├── test_models.py
│   │   └── test_api.py
│   └── management/        # Comandos custom
├── accounts/              # App de usuarios
│   ├── models.py          # CustomUser
│   └── views.py           # Auth views
├── frontend/              # React app
│   ├── src/
│   │   ├── pages/         # Páginas
│   │   ├── components/    # Componentes
│   │   └── context/       # Context API
│   └── package.json
├── .github/workflows/     # CI/CD
├── docker-compose.yml     # Docker config
├── requirements.txt       # Python deps
├── pytest.ini            # Pytest config
└── .env.example          # Env template
```

---

## 🔐 Seguridad

### Características Implementadas

- ✅ SECRET_KEY fuerte con validación
- ✅ Rate limiting (100/hora anon, 1000/hora auth)
- ✅ CORS configurado por entorno
- ✅ Autenticación JWT con expiración
- ✅ Permisos granulares por rol
- ✅ Validación de entrada
- ✅ Protección CSRF

### Recomendaciones para Producción

- [ ] Configurar SSL/TLS
- [ ] Implementar 2FA
- [ ] Configurar Sentry para error tracking
- [ ] Implementar backup automatizado
- [ ] Configurar firewall de aplicación

---

## 🚢 Deployment

### Con Docker Compose (Producción)

```bash
# 1. Configurar .env para producción
DEBUG=False
DJANGO_SECRET_KEY=<generar-nueva-key>
DATABASE_URL=postgresql://...
ALLOWED_HOSTS=tudominio.com

# 2. Build y ejecutar
docker-compose -f docker-compose.yml --profile production up --build -d

# 3. Ejecutar migraciones
docker-compose exec backend python manage.py migrate

# 4. Collectstatic
docker-compose exec backend python manage.py collectstatic --noinput
```

### Nginx

El proyecto incluye configuración de Nginx para reverse proxy. Ver `nginx.conf`.

---

## 📈 Performance

### Optimizaciones Implementadas

- ✅ Connection pooling en PostgreSQL
- ✅ Select/Prefetch related para evitar N+1 queries
- ✅ Paginación en todos los listados
- ✅ Índices de base de datos
- ✅ Multi-stage Docker builds

### Métricas Objetivo

- Response time API: < 200ms
- Frontend bundle: < 500KB
- Docker image: < 500MB
- Lighthouse score: ≥ 90

---

## 🤝 Contribuir

### Estándares de Código

- Backend: PEP 8
- Frontend: ESLint + Prettier
- Tests: Coverage mínimo 70%
- Commits: Conventional Commits

### Workflow

1. Fork el repositorio
2. Crear feature branch: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'feat: agregar nueva funcionalidad'`
4. Push al branch: `git push origin feature/nueva-funcionalidad`
5. Abrir Pull Request

---

## 📝 Changelog

### Version 1.0.0 (2026-01-09)

#### Added
- ✅ Configuración PostgreSQL con dj-database-url
- ✅ Rate limiting con DRF throttling
- ✅ Swagger/OpenAPI documentation
- ✅ Tests unitarios y de API (70%+ coverage)
- ✅ GitHub Actions CI/CD
- ✅ .env.example completo
- ✅ CORS seguro por entorno

#### Changed
- ✅ Mejorado SECRET_KEY con validación
- ✅ Actualizado requirements.txt
- ✅ Optimizado settings.py

---

## 📞 Soporte

### Documentación
- API Docs: `/api/docs/`
- Ver carpeta `/docs` para documentación técnica

### Comandos Útiles

```bash
# Generar SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Ejecutar tests
pytest

# Ejecutar con coverage
pytest --cov

# Crear migraciones
python manage.py makemigrations

# Ver logs Docker
docker-compose logs -f backend
```

---

## 📄 Licencia

[Especificar licencia]

---

## 👥 Autores

[Especificar autores]

---

**¡Gracias por usar GSIH Inventario!** 🎉