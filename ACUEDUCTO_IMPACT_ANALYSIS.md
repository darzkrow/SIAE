# Análisis de Impacto - Migración Acueducto → Subalmacén

**Fecha:** 4 de febrero de 2026  
**Proyecto:** QR Codes y Subalmacén  
**Rama:** `feature/qr-subalmacen`

---

## 🔍 Resumen Ejecutivo

### Modelos Acueducto Encontrados
1. **`institucion/models.py`** (línea 413) - `class Acueducto`
2. **`institucion/models.py`** (línea 2815) - `class AcueductoNuevo`

### Total de Referencias Encontradas
- **87 referencias** a "Acueducto" en archivos Python
- **45 referencias** a "acueducto" (lowercase) en archivos Python
- **Múltiples ForeignKeys** apuntando a Acueducto

---

## 📊 Análisis Detallado por Archivo

### 1. Modelos con ForeignKey a Acueducto

#### geography/models.py
```python
# Línea 56-61
acueducto = models.ForeignKey(
    Acueducto,
    on_delete=models.CASCADE,
    related_name='ubicaciones',
    null=True, blank=True
)
```
**Impacto:** Modelo `Ubicacion` tiene FK a Acueducto

#### inventario/models.py
```python
# Múltiples modelos Stock tienen FK a acueducto
class StockChemical:
    acueducto = models.ForeignKey(Acueducto, ...)

class StockPipe:
    acueducto = models.ForeignKey(Acueducto, ...)

class StockPumpAndMotor:
    acueducto = models.ForeignKey(Acueducto, ...)

class StockAccessory:
    acueducto = models.ForeignKey(Acueducto, ...)
```
**Impacto:** 4 modelos Stock tienen FK a Acueducto

#### notificaciones/models.py
```python
# Línea ~20
acueducto = models.ForeignKey(Acueducto, ...)
```
**Impacto:** Modelo `Alerta` tiene FK a Acueducto

---

## 📝 Referencias por Categoría

### A. Definiciones de Modelo (2)
1. `institucion/models.py:413` - `class Acueducto(models.Model)`
2. `institucion/models.py:2815` - `class AcueductoNuevo(models.Model)`

### B. ForeignKeys (7+ modelos)
1. `geography/models.py` - `Ubicacion.acueducto`
2. `inventario/models.py` - `StockChemical.acueducto`
3. `inventario/models.py` - `StockPipe.acueducto`
4. `inventario/models.py` - `StockPumpAndMotor.acueducto`
5. `inventario/models.py` - `StockAccessory.acueducto`
6. `notificaciones/models.py` - `Alerta.acueducto`
7. `institucion/models.py` - Posibles referencias internas

### C. Serializers (estimado 5-10)
- `geography/serializers.py`
- `inventario/serializers.py`
- `notificaciones/serializers.py`
- `institucion/serializers.py`

### D. ViewSets (estimado 5-10)
- `geography/views.py`
- `inventario/views.py`
- `notificaciones/views.py`
- `institucion/views.py`

### E. Admin (estimado 3-5)
- `geography/admin.py`
- `inventario/admin.py`
- `institucion/admin.py`

### F. Tests (estimado 10-20)
- Múltiples archivos de test en `institucion/tests/`
- Tests en `inventario/tests/`
- Tests en `geography/tests/`

---

## 🎯 Plan de Migración

### Fase 1: Crear Modelo Subalmacén
- [ ] Crear `Subalmacen` en `institucion/models.py`
- [ ] Incluir campos geográficos (estado, municipio, parroquia)
- [ ] Mantener compatibilidad con datos existentes

### Fase 2: Migración de Datos
- [ ] Crear migración de datos de `Acueducto` → `Subalmacen`
- [ ] Asignar estados/municipios a subalmacenes existentes
- [ ] Validar integridad de datos

### Fase 3: Actualizar ForeignKeys (7 modelos)
1. [ ] `geography.Ubicacion.acueducto` → `subalmacen`
2. [ ] `inventario.StockChemical.acueducto` → `subalmacen`
3. [ ] `inventario.StockPipe.acueducto` → `subalmacen`
4. [ ] `inventario.StockPumpAndMotor.acueducto` → `subalmacen`
5. [ ] `inventario.StockAccessory.acueducto` → `subalmacen`
6. [ ] `notificaciones.Alerta.acueducto` → `subalmacen`
7. [ ] Otras referencias internas en `institucion`

### Fase 4: Actualizar Serializers
- [ ] Actualizar imports de `Acueducto` → `Subalmacen`
- [ ] Agregar campos geográficos a serializers
- [ ] Actualizar campos relacionados

### Fase 5: Actualizar ViewSets
- [ ] Actualizar filtros y búsquedas
- [ ] Agregar query optimization para campos geográficos
- [ ] Actualizar permisos si es necesario

### Fase 6: Actualizar Admin
- [ ] Renombrar `AcueductoAdmin` → `SubalmacenAdmin`
- [ ] Agregar filtros por estado/municipio
- [ ] Actualizar formularios

### Fase 7: Actualizar Tests
- [ ] Actualizar fixtures
- [ ] Actualizar factories
- [ ] Actualizar assertions
- [ ] Validar todos los tests pasan

### Fase 8: Deprecar Acueducto
- [ ] Marcar `Acueducto` como deprecated
- [ ] Crear alias temporal para compatibilidad
- [ ] Planificar eliminación futura

---

## ⚠️ Riesgos Identificados

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Pérdida de datos en migración | Media | Alto | Backup completo + validación |
| ForeignKeys rotas | Alta | Alto | Migración cuidadosa de FK |
| Tests fallidos | Alta | Medio | Actualizar tests gradualmente |
| Incompatibilidad con frontend | Media | Medio | Mantener nombres de campos |
| Dos modelos Acueducto | Alta | Medio | Unificar en un solo Subalmacen |

---

## 📈 Estimación de Esfuerzo

| Tarea | Archivos Afectados | Tiempo Estimado |
|-------|-------------------|-----------------|
| Crear modelo Subalmacén | 1 | 2 horas |
| Migración de datos | 2-3 | 3 horas |
| Actualizar ForeignKeys | 7 modelos | 4 horas |
| Actualizar Serializers | 5-10 | 2 horas |
| Actualizar ViewSets | 5-10 | 2 horas |
| Actualizar Admin | 3-5 | 1 hora |
| Actualizar Tests | 10-20 | 4 horas |
| Documentación | - | 2 horas |
| **TOTAL** | **30-50 archivos** | **20 horas** |

---

## 🔧 Archivos Críticos a Modificar

### Alta Prioridad (Rompen funcionalidad)
1. `institucion/models.py` - Definición de Subalmacén
2. `geography/models.py` - FK en Ubicacion
3. `inventario/models.py` - FK en Stock models
4. `notificaciones/models.py` - FK en Alerta
5. Migraciones de Django

### Media Prioridad (Afectan API)
6. `institucion/serializers.py`
7. `geography/serializers.py`
8. `inventario/serializers.py`
9. `notificaciones/serializers.py`
10. ViewSets correspondientes

### Baja Prioridad (No rompen funcionalidad)
11. Admin files
12. Tests
13. Documentación

---

## ✅ Criterios de Aceptación

### Migración Exitosa
- [ ] Todos los datos de Acueducto migrados a Subalmacén
- [ ] Todas las ForeignKeys actualizadas
- [ ] No hay pérdida de datos
- [ ] Todos los tests pasan

### Funcionalidad
- [ ] API endpoints funcionan correctamente
- [ ] Filtros por ubicación geográfica funcionan
- [ ] Admin permite gestionar subalmacenes
- [ ] Frontend puede consumir nuevos endpoints

### Calidad
- [ ] Cobertura de tests >80%
- [ ] Documentación actualizada
- [ ] No hay warnings en migraciones
- [ ] Query optimization implementado

---

## 📝 Notas Adicionales

### Observaciones Importantes
1. **Dos modelos Acueducto:** Existe `Acueducto` y `AcueductoNuevo` en institucion. Necesitamos unificar.
2. **Ubicación actual:** Campo `ubicacion` en Acueducto es CharField, no FK geográfica.
3. **Stock models:** 4 modelos diferentes de stock tienen FK a acueducto.
4. **Related names:** Verificar que `related_name` sea consistente.

### Decisiones Pendientes
- [ ] ¿Mantener modelo Acueducto temporalmente?
- [ ] ¿Crear alias `Acueducto = Subalmacen`?
- [ ] ¿Migrar AcueductoNuevo también?
- [ ] ¿Asignar estados manualmente o automáticamente?

---

**Próximo Paso:** Crear modelo Subalmacén con campos geográficos
