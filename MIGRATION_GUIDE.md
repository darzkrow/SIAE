# 🔧 Guía de Migraciones - Fase 4

## ⚠️ IMPORTANTE: Migraciones Pendientes

Los modelos han sido refactorizados para usar clases base de `core`, pero **las migraciones de Django aún no se han generado**.

---

## 📋 Pasos para Generar y Aplicar Migraciones

### 1. Activar Entorno Virtual

```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Generar Migraciones

```bash
cd backend

# Apps completadas (Fase 4 Parcial)
python manage.py makemigrations accounts --name migrate_to_core_timestamped
python manage.py makemigrations catalogo --name migrate_to_core_softdelete
python manage.py makemigrations compras --name migrate_to_core_base_classes

# Apps pendientes (cuando se completen)
# python manage.py makemigrations inventario --name migrate_to_core_base_classes
# python manage.py makemigrations institucion --name migrate_to_core_base_classes
```

### 3. Revisar Migraciones Generadas

```bash
# Ver las migraciones creadas
ls accounts/migrations/
ls catalogo/migrations/
ls compras/migrations/
```

**Verificar que:**
- No hay pérdida de datos
- Los campos duplicados se eliminan correctamente
- Los nuevos campos tienen valores por defecto apropiados

### 4. Aplicar Migraciones

```bash
# Aplicar en orden de dependencias
python manage.py migrate accounts
python manage.py migrate catalogo
python manage.py migrate compras

# Cuando estén listas
# python manage.py migrate inventario
# python manage.py migrate institucion
```

### 5. Verificar Integridad

```bash
# Verificar que no hay problemas
python manage.py check

# Verificar migraciones aplicadas
python manage.py showmigrations
```

---

## 📊 Modelos Refactorizados (Fase 4 Parcial)

### ✅ Accounts (4 modelos)
- `Permission` → `TimeStampedModel`
- `Role` → `TimeStampedModel`
- `RolePermission` → `TimeStampedModel`
- `UserRole` → `TimeStampedModel`

**Cambios:**
- Eliminados campos `created_at` y `updated_at` duplicados
- Ahora heredan de `core.models.TimeStampedModel`
- `UserRole.assigned_at` → `UserRole.created_at`

### ✅ Catalogo (2 modelos)
- `CategoriaProducto` → `core.SoftDeleteModel`
- `Marca` → `core.SoftDeleteModel`

**Cambios:**
- Migrados de `auditoria.models.SoftDeleteModel` a `core.models.SoftDeleteModel`
- Ahora usan la implementación centralizada de core

### ✅ Compras (3 modelos)
- `Correlativo` → `TimeStampedModel`
- `OrdenCompra` → `core.SoftDeleteModel`
- `ItemOrden` → `core.SoftDeleteModel`

**Cambios:**
- `Correlativo` ahora tiene timestamps automáticos
- `OrdenCompra` e `ItemOrden` migrados a core.SoftDeleteModel

---

## ⏳ Modelos Pendientes

### Inventario (~15 modelos)
- OrganizacionCentral, Sucursal, Acueducto
- UnitOfMeasure, Supplier
- ChemicalProduct, Pipe, PumpAndMotor, Accessory
- StockChemical, StockPipe, StockPumpAndMotor, StockAccessory
- MovimientoInventario
- FichaTecnicaMotor, RegistroMantenimiento

### Institucion (~10 modelos)
- Empresa, Vicepresidencia, UnidadOrganizacional, AlmacenRegional
- ActivoInventario, HistorialMovimientoActivo
- SolicitudTraslado, AprobacionTraslado
- OrganizacionCentral, Sucursal, Acueducto (legacy)

---

## 🚨 Notas Importantes

### Cambios en Campos

#### UserRole
```python
# ANTES
assigned_at = models.DateTimeField(auto_now_add=True)
ordering = ['-assigned_at']

# DESPUÉS
# created_at heredado de TimeStampedModel
ordering = ['-created_at']
```

**Impacto:** Cualquier código que use `assigned_at` debe cambiarse a `created_at`.

#### Modelos de Catalogo y Compras
```python
# ANTES
from auditoria.models import SoftDeleteModel

# DESPUÉS
from core.models import SoftDeleteModel
```

**Impacto:** Mismo comportamiento, solo cambió la ubicación.

---

## ✅ Verificación Post-Migración

### Tests a Ejecutar

```bash
# Verificar que los modelos funcionan
python manage.py shell

>>> from accounts.models import Permission, Role
>>> from catalogo.models import CategoriaProducto
>>> from compras.models import OrdenCompra

# Verificar timestamps automáticos
>>> perm = Permission.objects.create(
...     name="Test",
...     codename="test",
...     content_type_id=1
... )
>>> print(perm.created_at)  # Debe tener valor
>>> print(perm.updated_at)  # Debe tener valor

# Verificar soft delete
>>> cat = CategoriaProducto.objects.create(nombre="Test", codigo="TST")
>>> cat.delete()  # Soft delete
>>> print(cat.deleted_at)  # Debe tener valor
>>> cat.restore()  # Restaurar
>>> print(cat.deleted_at)  # Debe ser None
```

### Queries a Verificar

```python
# Verificar que los managers funcionan
>>> CategoriaProducto.objects.all()  # Solo no eliminados
>>> CategoriaProducto.all_objects.all()  # Todos incluidos eliminados
>>> CategoriaProducto.objects.deleted()  # Solo eliminados
```

---

## 📝 Próximos Pasos

1. ✅ **Generar migraciones** para accounts, catalogo, compras
2. ✅ **Aplicar migraciones** en desarrollo
3. ✅ **Verificar** que todo funciona correctamente
4. ⏳ **Continuar** con inventario e institucion
5. ⏳ **Generar migraciones** para inventario e institucion
6. ⏳ **Aplicar todas las migraciones** en producción

---

**Fecha:** 4 de febrero de 2026  
**Estado:** Fase 4 Parcial Completada (3/5 apps)  
**Progreso:** 9/33+ modelos refactorizados (27%)
