# SIAE - Sistema Integrado de Administración de Empresas

Sistema completo de gestión empresarial con módulos de inventario, compras, catálogo, auditoría y reestructuración organizacional Hidroven.

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
│   ├── accounts/      # Autenticación y usuarios
│   ├── institucion/   # Módulo Hidroven
│   ├── inventario/    # Gestión de inventario
│   ├── compras/       # Gestión de compras
│   ├── catalogo/      # Catálogo de productos
│   ├── auditoria/     # Sistema de auditoría
│   └── notificaciones/# Sistema de notificaciones
├── frontend/          # React + Vite
├── docs-archive/      # Documentación histórica
└── .kiro/            # Especificaciones del proyecto
```

## 📚 Documentación

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
```

## 📊 Estado del Proyecto

✅ **Sistema Hidroven:** Completamente implementado y testeado
- 13 grupos de tareas completadas
- 208 tests implementados
- 16 property-based tests
- 6 integration tests end-to-end

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es privado y confidencial.

## 📧 Contacto

Para más información, consulta la documentación en [`docs-archive/`](docs-archive/README.md)

---

**Última actualización:** Febrero 2026