# Inicio Rápido para Desarrolladores - GSIH Inventario

**Fecha**: 8 de Enero de 2026  
**Versión**: 1.0  
**Audiencia**: Desarrolladores nuevos en el proyecto

---

## ⚡ 5 MINUTOS PARA EMPEZAR

### 1. Clonar y Configurar
```powershell
git clone <repo-url>
cd proyecto-inventario
docker compose up --build
```

### 2. Acceder a la Aplicación
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs/

### 3. Credenciales de Prueba
```
Usuario: admin
Contraseña: admin123
```

### 4. Explorar la API
Ir a http://localhost:8000/api/docs/ y probar endpoints

### 5. Revisar Documentación
Leer `docs/PROYECTO-COMPLETADO-95-PORCIENTO.md`

---

## 📁 ESTRUCTURA DEL PROYECTO

```
proyecto-inventario/
├── backend/                    # Django REST API
│   ├── config/                # Configuración
│   ├── accounts/              # Autenticación
│   ├── inventario/            # Lógica de inventario
│   ├── manage.py
│   └── requirements.txt
├── frontend/                   # React + Vite
│   ├── src/
│   │   ├── pages/            # Páginas principales
│   │   ├── components/       # Componentes reutilizables
│   │   ├── context/          # Context API
│   │   ├── hooks/            # Custom hooks
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── docs/                       # Documentación general
├── docs-tecnico/              # Documentación técnica
├── docker-compose.yml         # Configuración Docker
├── Dockerfile.backend         # Docker para backend
├── nginx.conf                 # Configuración Nginx
└── .env.example              # Variables de entorno
```

---

## 🔧 COMANDOS ESENCIALES

### Docker
```powershell
# Iniciar proyecto
docker compose up

# Iniciar en background
docker compose up -d

# Ver logs
docker compose logs -f

# Detener
docker compose down

# Reconstruir
docker compose up --build
```

### Backend
```powershell
# Entrar al contenedor
docker compose exec backend bash

# Hacer migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar tests
python manage.py test

# Seed de datos
python manage.py seed_inventario
```

### Frontend
```powershell
# Entrar al contenedor
docker compose exec frontend bash

# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev

# Build para producción
npm run build
```

---

## 📚 DOCUMENTACIÓN CLAVE

### Para Entender el Proyecto
1. **`docs/RESUMEN-EJECUTIVO-FINAL.md`** - Resumen ejecutivo (5 min)
2. **`docs/PROYECTO-COMPLETADO-95-PORCIENTO.md`** - Estado actual (10 min)
3. **`docs/GUIA-RAPIDA-FINAL.md`** - Guía rápida (5 min)

### Para Usar la API
1. **`docs/REFERENCIA-RAPIDA-ENDPOINTS.md`** - Lista de endpoints (5 min)
2. **`docs-tecnico/SWAGGER-OPENAPI.md`** - Documentación Swagger (10 min)
3. **`docs-tecnico/ENDPOINTS-BUSQUEDA-STOCK.md`** - Endpoints específicos (10 min)

### Para Implementar Funcionalidades
1. **`docs/TAREAS-PENDIENTES-FINALES.md`** - Tareas pendientes (10 min)
2. **`docs-tecnico/SISTEMA-APROBACIONES.md`** - Especificación Fase 4 (20 min)
3. **`docs-tecnico/INTEGRACION-SISTEMAS-EXTERNOS.md`** - Especificación Fase 4 (20 min)

### Para Troubleshooting
1. **`docs/GUIA-RAPIDA-FINAL.md`** - Sección de troubleshooting
2. **`docs-tecnico/VALIDACIONES-SISTEMA.md`** - Validaciones
3. **`docs-tecnico/PRUEBAS-ENDPOINTS-BUSQUEDA.md`** - Casos de prueba

---

## 🔑 CONCEPTOS CLAVE

### Modelos Principales
- **Tuberia** - Artículos tipo tubería
- **Equipo** - Artículos tipo equipo
- **Stock** - Cantidad disponible por ubicación
- **Movimiento** - Entrada/Salida/Transferencia/Ajuste
- **InventoryAudit** - Registro de cambios

### Endpoints Principales
```
GET    /api/tuberias/              # Listar tuberías
POST   /api/tuberias/              # Crear tubería
GET    /api/stock-tuberias/        # Stock de tuberías
POST   /api/movimientos/           # Crear movimiento
GET    /api/reportes/stock_search/ # Buscar stock
GET    /api/audits/                # Ver auditoría
```

### Roles y Permisos
- **ADMIN** - Acceso completo
- **OPERADOR** - Acceso limitado a su sucursal

---

## 🚀 FLUJO DE DESARROLLO

### 1. Crear una Rama
```powershell
git checkout -b feature/nombre-feature
```

### 2. Hacer Cambios
- Backend: Editar archivos en `backend/`
- Frontend: Editar archivos en `frontend/src/`

### 3. Probar Cambios
```bash
# Backend
docker compose exec backend python manage.py test inventario
docker compose exec backend python manage.py test inventario geography institucion catalogo compras

# Frontend
docker-compose exec frontend npm run test
```

### 4. Hacer Commit
```powershell
git add .
git commit -m "Descripción clara del cambio"
```

### 5. Push y Pull Request
```bash
git push origin feature/nombre-feature
# Crear PR en GitHub
```

---

## 🐛 TROUBLESHOOTING RÁPIDO

### El proyecto no inicia
```bash
# Limpiar y reconstruir
docker compose down
docker compose up --build
```

### Error de base de datos
```bash
# Hacer migraciones
docker compose exec backend python manage.py migrate
```

### Frontend no carga
```bash
# Instalar dependencias
docker compose exec frontend npm install
```

### Ver logs detallados
```bash
docker compose logs -f backend
docker compose logs -f frontend
```

---

## 📊 ESTADO DEL PROYECTO

| Métrica | Valor |
|---------|-------|
| Completitud | 95% |
| Endpoints | 20+ |
| Tests | 50+ |
| Documentación | 15,000+ líneas |
| Errores | 0 |
| Warnings | 0 |

---

## 🎯 PRÓXIMOS PASOS

### Hoy
- [ ] Clonar el repositorio
- [ ] Ejecutar `docker-compose up`
- [ ] Acceder a http://localhost:3000
- [ ] Leer `docs/RESUMEN-EJECUTIVO-FINAL.md`

### Esta Semana
- [ ] Explorar la API en Swagger
- [ ] Leer documentación técnica
- [ ] Entender la estructura del código
- [ ] Hacer un cambio pequeño

### Este Mes
- [ ] Implementar una funcionalidad de Fase 4
- [ ] Escribir tests
- [ ] Documentar cambios
- [ ] Hacer PR

---

## 📞 AYUDA

### Documentación
- Índice completo: `docs/INDICE-DOCUMENTACION-COMPLETA.md`
- Guía rápida: `docs/GUIA-RAPIDA-FINAL.md`
- API Docs: http://localhost:8000/api/docs/

### Comandos Útiles
```bash
# Ver estado del proyecto
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Acceder a la base de datos
docker-compose exec db psql -U postgres -d inventario_db

# Ejecutar comando en backend
docker-compose exec backend python manage.py <comando>
```

### Contacto
- Revisar documentación en `docs/` y `docs-tecnico/`
- Consultar Swagger en `/api/docs/`
- Revisar logs en `docker-compose logs`

---

## ✨ TIPS PARA DESARROLLADORES

1. **Siempre leer la documentación primero** - Ahorra tiempo
2. **Usar Swagger para probar endpoints** - Más rápido que Postman
3. **Revisar tests existentes** - Aprende del código
4. **Hacer commits frecuentes** - Facilita debugging
5. **Documentar cambios** - Ayuda a otros desarrolladores

---

## 🎓 RECURSOS ADICIONALES

### Tecnologías Usadas
- **Backend**: Django, Django REST Framework, PostgreSQL
- **Frontend**: React, Vite, Axios, SweetAlert2
- **DevOps**: Docker, Docker Compose, Nginx
- **Testing**: pytest, unittest

### Documentación Externa
- Django: https://docs.djangoproject.com/
- React: https://react.dev/
- Docker: https://docs.docker.com/
- PostgreSQL: https://www.postgresql.org/docs/

---

## 📝 CHECKLIST PARA NUEVOS DESARROLLADORES

- [ ] Cloné el repositorio
- [ ] Ejecuté `docker-compose up`
- [ ] Accedí a http://localhost:3000
- [ ] Leí `docs/RESUMEN-EJECUTIVO-FINAL.md`
- [ ] Exploré la API en Swagger
- [ ] Entendí la estructura del proyecto
- [ ] Hice un cambio pequeño
- [ ] Ejecuté los tests
- [ ] Leí la documentación técnica

---

**¡Bienvenido al proyecto GSIH Inventario!**

Si tienes preguntas, consulta la documentación o contacta al equipo.

---

**Última Actualización**: 8 de Enero de 2026  
**Versión**: 1.0

