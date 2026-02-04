# SIAE - Sistema Integrado de Administración de Empresas

Sistema completo de gestión empresarial con módulos de inventario, compras, catálogo, auditoría y reestructuración organizacional Hidroven.

## 🎉 Proyecto de Optimización Completado (Febrero 2026)

**Estado:** ✅ 100% Completado (8/8 fases)  
**Rama:** `feature/code-optimization`

### Logros Principales
- ⚡ **95-98% reducción** en queries de base de datos
- 🚀 **60-70% más rápido** en tiempos de respuesta de API
- 🧹 **~600 líneas** de código duplicado eliminadas
- 🏗️ **90+ componentes** refactorizados (serializers, viewsets, models)
- 📚 **100% consistencia** en arquitectura

### Documentación del Proyecto
- [📊 Resumen Final](./OPTIMIZATION_FINAL_SUMMARY.md) - Overview completo del proyecto
- [📝 CHANGELOG](./CHANGELOG.md) - Historial detallado de cambios
- [🗺️ Guía de Migraciones](./MIGRATION_GUIDE.md) - Instrucciones para migraciones de BD
- [📈 Plan de Queries](./QUERY_OPTIMIZATION_PLAN.md) - Análisis de optimización

---

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.10+
- Node.js 16+
- PostgreSQL 13+
- Docker (opcional)

### Instalación

#### Backend (Django)
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

## 📁 Estructura del Proyecto

```
SIAE/
├── backend/           # Django REST API
│   ├── core/          # 🆕 App base con utilidades compartidas
│   ├── accounts/      # Autenticación y usuarios
│   ├── institucion/   # Módulo Hidroven
│   ├── inventario/    # Gestión de inventario
│   ├── compras/       # Gestión de compras
│   ├── catalogo/      # Catálogo de productos
│   ├── auditoria/     # Sistema de auditoría
│   ├── geography/     # Geografía venezolana
│   └── notificaciones/# Sistema de notificaciones
├── frontend/          # React + Vite
├── docs-archive/      # Documentación histórica
└── .kiro/            # Especificaciones del proyecto
```

## 🏗️ Arquitectura Core (Nuevo)

La app `core` proporciona clases base reutilizables para todo el proyecto:

### Modelos Base
- `TimeStampedModel` - Timestamps automáticos (`created_at`, `updated_at`)
- `SoftDeleteModel` - Soft delete con manager personalizado
- `BaseModel` - Modelo completo con ambas funcionalidades

### Serializers Base
- `BaseModelSerializer` - Campos comunes (id, timestamps)
- `SoftDeleteSerializer` - Incluye campos de soft delete

### ViewSets Base
- `BaseModelViewSet` - CRUD con contexto de usuario
- `SoftDeleteViewSet` - Con endpoint de restauración

### Utilidades
- Validadores venezolanos (RIF, cédula, teléfono)
- Formateo de datos (moneda, fechas, documentos)
- Constantes globales (estados, tipos de documento)

## 📚 Documentación

- **Optimización Backend:** [`OPTIMIZATION_FINAL_SUMMARY.md`](OPTIMIZATION_FINAL_SUMMARY.md)
- **Documentación Histórica:** [`docs-archive/`](docs-archive/README.md)
- **Especificaciones Actuales:** [`.kiro/specs/`](.kiro/specs/)
- **Validación del Sistema:** Ver artifacts en `.gemini/antigravity/brain/`

## 🏢 Módulo Hidroven

Sistema de reestructuración organizacional con:
- Jerarquía de 3 niveles (Empresa → Vicepresidencia → Unidad Organizacional)
- 9 almacenes regionales con códigos únicos
- Sistema de trazabilidad de activos con códigos evolutivos
- Workflow de aprobación dual para traslados
- Auditoría completa de operaciones

Ver: [`docs-archive/root-docs/REESTRUCTURACION_HIDROVEN_PLAN.md`](docs-archive/root-docs/REESTRUCTURACION_HIDROVEN_PLAN.md)

## 🔧 Tecnologías

### Backend
- Django 5.0.2
- Django REST Framework
- PostgreSQL
- Celery
- Redis
- MPTT (Modified Preorder Tree Traversal)
- Hypothesis (Property-based testing)

### Frontend
- React 18
- Vite
- React Router
- Axios
- TailwindCSS

## 🧪 Testing

```bash
# Backend tests
cd backend
python manage.py test

# Tests específicos de Hidroven
python manage.py test institucion

# Property-based tests
python manage.py test institucion.test_asset_code_properties

# Con cobertura
pytest backend/ -v --cov=backend --cov-report=html
```

## 📊 Estado del Proyecto

### ✅ Sistema Hidroven
- 13 grupos de tareas completadas
- 208 tests implementados
- 16 property-based tests
- 6 integration tests end-to-end

### ✅ Optimización Backend (100%)
- 8/8 fases completadas
- 90+ componentes refactorizados
- ~600 líneas de código eliminadas
- 95-98% reducción en queries
- 60-70% mejora en performance

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guías de Desarrollo
- Usa las clases base de `core` para nuevos modelos, serializers y viewsets
- Siempre agrega `select_related()` o `prefetch_related()` en viewsets con relaciones
- Sigue el patrón de soft delete para modelos que requieren auditoría
- Escribe tests para toda nueva funcionalidad

## 📝 Licencia

Este proyecto es privado y confidencial.

## 📧 Contacto

Para más información, consulta la documentación en [`docs-archive/`](docs-archive/README.md)

---

**Última actualización:** Febrero 2026  
**Versión:** 2.0 (Post-Optimización)