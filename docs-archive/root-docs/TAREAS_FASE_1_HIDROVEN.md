# 📋 FASE 1: Análisis y Diseño - Reestructuración Hidroven

## 🎯 Objetivo de la Fase
Analizar la estructura actual y diseñar los nuevos modelos organizacionales para implementar la jerarquía de Hidroven manteniendo la lógica de negocio existente.

---

## 📝 **TAREA 1.1: Diseño del Nuevo Modelo Organizacional**

### **Información General**
- **Complejidad**: ⭐⭐⭐⭐⭐ (Alta)
- **Tiempo Estimado**: 3-4 días
- **Prioridad**: Crítica
- **Dependencias**: Ninguna

### **Descripción**
Diseñar e implementar los nuevos modelos Django que representen la estructura organizacional de Hidroven con sus vicepresidencias y jerarquía completa.

### **Subtareas Detalladas**

#### **1.1.1 Crear modelo `Empresa` (Hidroven)**
**Tiempo**: 4 horas  
**Responsable**: Backend Developer

**Especificaciones**:
- Modelo principal que representa Hidroven
- Campos requeridos: nombre, RIF, presidente, dirección, teléfono, email
- Relación con User para presidente (máxima autoridad)
- Validaciones: RIF único, presidente único por empresa
- Soft delete habilitado
- Auditoría completa

**Criterios de Aceptación**:
- [ ] Modelo creado con todos los campos especificados
- [ ] Validaciones implementadas y funcionando
- [ ] Tests unitarios creados (mínimo 5 casos)
- [ ] Documentación del modelo actualizada

**Archivos a Modificar**:
- `backend/institucion/models.py` (agregar nuevo modelo)
- `backend/institucion/admin.py` (registrar en admin)
- `backend/institucion/tests/test_models.py` (tests)

#### **1.1.2 Crear modelo `Vicepresidencia` con tipos específicos**
**Tiempo**: 6 horas  
**Responsable**: Backend Developer

**Especificaciones**:
- Tres tipos específicos: Comercialización, Operaciones Hídricas, Administrativa
- Relación con Empresa (ForeignKey)
- Relación con User para vicepresidente
- Campos: tipo, nombre, código, descripción
- Constraint: solo una VP de cada tipo por empresa
- Métodos calculados: total_unidades, total_acueductos

**Criterios de Aceptación**:
- [ ] Modelo con TextChoices para tipos de VP
- [ ] Constraints de unicidad implementados
- [ ] Métodos de cálculo funcionando
- [ ] Auto-generación de códigos (VP-COM, VP-OPE, VP-ADM)
- [ ] Tests para todos los tipos de VP

**Archivos a Modificar**:
- `backend/institucion/models.py`
- `backend/institucion/admin.py`
- `backend/institucion/tests/test_models.py`

#### **1.1.3 Crear modelo `UnidadOrganizacional` (genérico)**
**Tiempo**: 8 horas  
**Responsable**: Backend Developer

**Especificaciones**:
- Modelo genérico para direcciones, gerencias, coordinaciones, etc.
- Tipos: DIRECCION, GERENCIA, COORDINACION, DEPARTAMENTO, DIVISION, OFICINA
- Relación jerárquica (self-referencing FK para parent)
- Relación con Vicepresidencia
- Campos: tipo, nombre, código, responsable, descripción
- Métodos: nivel_jerarquico, ruta_jerarquica

**Criterios de Aceptación**:
- [ ] Jerarquía interna funcionando correctamente
- [ ] Validaciones para evitar referencias circulares
- [ ] Métodos de navegación jerárquica implementados
- [ ] Tests para diferentes niveles de jerarquía

**Archivos a Modificar**:
- `backend/institucion/models.py`
- `backend/institucion/admin.py`
- `backend/institucion/tests/test_models.py`

#### **1.1.4 Rediseñar modelo `Acueducto` para nueva jerarquía**
**Tiempo**: 6 horas  
**Responsable**: Backend Developer

**Especificaciones**:
- Nuevo modelo `AcueductoNuevo` con relación a UnidadOrganizacional
- Tipos de sistema: ACUEDUCTO, PLANTA, BOMBEO, EMBALSE, POZO
- Campos adicionales: capacidad_produccion, poblacion_servida
- Propiedades calculadas: vicepresidencia, empresa, ruta_organizacional_completa
- Mantener compatibilidad con modelo anterior durante transición

**Criterios de Aceptación**:
- [ ] Nuevo modelo completamente funcional
- [ ] Propiedades calculadas funcionando
- [ ] Tipos de sistema bien definidos
- [ ] Compatibilidad con inventario existente

**Archivos a Modificar**:
- `backend/institucion/models.py`
- `backend/institucion/admin.py`
- `backend/institucion/tests/test_models.py`

#### **1.1.5 Crear modelo `Responsable` para asignación de autoridades**
**Tiempo**: 4 horas  
**Responsable**: Backend Developer

**Especificaciones**:
- Modelo para gestionar responsabilidades y delegaciones
- Relaciones con User y diferentes niveles organizacionales
- Campos: usuario, nivel_organizacional, fecha_inicio, fecha_fin
- Validaciones: no solapamiento de responsabilidades

**Criterios de Aceptación**:
- [ ] Modelo de responsabilidades implementado
- [ ] Validaciones de solapamiento funcionando
- [ ] Historial de responsabilidades mantenido

**Archivos a Modificar**:
- `backend/institucion/models.py`
- `backend/institucion/admin.py`
- `backend/institucion/tests/test_models.py`

#### **1.1.6 Definir relaciones y constraints de integridad**
**Tiempo**: 4 horas  
**Responsable**: Backend Developer

**Especificaciones**:
- Definir todas las relaciones entre modelos
- Implementar constraints de integridad referencial
- Configurar cascadas y protecciones
- Documentar todas las relaciones

**Criterios de Aceptación**:
- [ ] Todas las relaciones definidas correctamente
- [ ] Constraints de integridad implementados
- [ ] Cascadas configuradas apropiadamente
- [ ] Documentación de relaciones completa

**Archivos a Modificar**:
- `backend/institucion/models.py`
- `docs/MODELO_ORGANIZACIONAL.md` (nuevo)

### **Entregables de la Tarea 1.1**
1. **Modelos Django implementados**:
   - `Empresa`
   - `Vicepresidencia`
   - `UnidadOrganizacional`
   - `AcueductoNuevo`
   - `Responsable`

2. **Migraciones Django**:
   - Migración inicial con todos los modelos
   - Índices optimizados
   - Constraints de integridad

3. **Tests Unitarios**:
   - Cobertura mínima 85%
   - Tests para todos los modelos
   - Tests de validaciones
   - Tests de relaciones

4. **Documentación**:
   - Diagrama ER actualizado
   - Documentación de modelos
   - Guía de relaciones

---

## 📝 **TAREA 1.2: Análisis de Impacto en Sistema Existente**

### **Información General**
- **Complejidad**: ⭐⭐⭐ (Media)
- **Tiempo Estimado**: 2 días
- **Prioridad**: Alta
- **Dependencias**: Tarea 1.1

### **Descripción**
Analizar el impacto de los nuevos modelos en el sistema existente, identificando todos los puntos que requieren modificación.

### **Subtareas Detalladas**

#### **1.2.1 Mapear todas las referencias a `OrganizacionCentral`**
**Tiempo**: 4 horas  
**Responsable**: Backend Developer

**Especificaciones**:
- Buscar todas las referencias en el código
- Identificar ForeignKeys, queries, filtros
- Documentar cada uso y su propósito
- Clasificar por criticidad de cambio

**Criterios de Aceptación**:
- [ ] Lista completa de referencias encontradas
- [ ] Clasificación por tipo de uso
- [ ] Evaluación de impacto por referencia
- [ ] Plan de modificación para cada caso

**Herramientas**:
```bash
# Buscar referencias en código Python
grep -r "OrganizacionCentral" backend/
grep -r "organizacion_central" backend/

# Buscar en templates y frontend
grep -r "organizacion" frontend/
```

#### **1.2.2 Identificar queries que necesitan actualización**
**Tiempo**: 4 horas  
**Responsable**: Backend Developer

**Especificaciones**:
- Revisar ViewSets y queries existentes
- Identificar filtros por organización
- Analizar joins y select_related
- Documentar queries complejas

**Criterios de Aceptación**:
- [ ] Lista de queries que requieren cambios
- [ ] Análisis de rendimiento de nuevas queries
- [ ] Plan de optimización
- [ ] Identificación de índices necesarios

**Archivos a Revisar**:
- `backend/inventario/views.py`
- `backend/inventario/filters.py`
- `backend/accounts/views.py`
- Todos los ViewSets que filtran por organización

#### **1.2.3 Analizar impacto en permisos y filtros**
**Tiempo**: 4 horas  
**Responsable**: Backend Developer

**Especificaciones**:
- Revisar sistema de permisos actual
- Identificar filtros por sucursal/organización
- Analizar middleware de permisos
- Planificar nuevos permisos jerárquicos

**Criterios de Aceptación**:
- [ ] Análisis completo del sistema de permisos
- [ ] Identificación de cambios necesarios
- [ ] Plan para permisos jerárquicos
- [ ] Estrategia de migración de permisos

**Archivos a Revisar**:
- `backend/inventario/permissions.py`
- `backend/accounts/permissions.py`
- Middleware de auditoría

#### **1.2.4 Revisar serializers y ViewSets afectados**
**Tiempo**: 3 horas  
**Responsable**: Backend Developer

**Especificaciones**:
- Identificar serializers que incluyen organización
- Revisar ViewSets con filtros organizacionales
- Analizar endpoints de reportes
- Planificar cambios en API

**Criterios de Aceptación**:
- [ ] Lista de serializers a modificar
- [ ] Plan de cambios en ViewSets
- [ ] Estrategia para mantener compatibilidad API
- [ ] Documentación de cambios en endpoints

#### **1.2.5 Documentar cambios necesarios en frontend**
**Tiempo**: 3 horas  
**Responsable**: Frontend Developer

**Especificaciones**:
- Identificar componentes que muestran organización
- Revisar servicios API afectados
- Analizar formularios de administración
- Planificar nuevos componentes organizacionales

**Criterios de Aceptación**:
- [ ] Lista de componentes a modificar
- [ ] Plan de nuevos componentes
- [ ] Estrategia de migración de UI
- [ ] Mockups de nuevas interfaces

### **Entregables de la Tarea 1.2**
1. **Reporte de Impacto**:
   - Análisis completo de referencias
   - Clasificación por criticidad
   - Estimación de esfuerzo por cambio

2. **Lista de Archivos a Modificar**:
   - Backend: modelos, views, serializers, permisos
   - Frontend: componentes, servicios, páginas

3. **Plan de Migración de Datos**:
   - Estrategia de migración
   - Scripts necesarios
   - Plan de rollback

4. **Documentación Técnica**:
   - Análisis de queries
   - Plan de optimización
   - Estrategia de compatibilidad

---

## 🎯 **Criterios de Éxito de la Fase 1**

### **Técnicos**
- [ ] Todos los modelos nuevos implementados y probados
- [ ] Análisis de impacto completo y documentado
- [ ] Migraciones Django creadas y validadas
- [ ] Tests unitarios con cobertura ≥ 85%
- [ ] Documentación técnica actualizada

### **Funcionales**
- [ ] Estructura organizacional de Hidroven modelada correctamente
- [ ] Jerarquía de vicepresidencias implementada
- [ ] Compatibilidad con sistema existente mantenida
- [ ] Plan de migración validado

### **Calidad**
- [ ] Código revisado y aprobado
- [ ] Estándares de codificación seguidos
- [ ] Documentación completa y clara
- [ ] Tests pasando al 100%

---

## 📅 **Cronograma Detallado**

| Día | Tarea | Responsable | Entregables |
|-----|-------|-------------|-------------|
| 1 | 1.1.1, 1.1.2 | Backend Dev | Modelos Empresa y Vicepresidencia |
| 2 | 1.1.3 | Backend Dev | Modelo UnidadOrganizacional |
| 3 | 1.1.4, 1.1.5 | Backend Dev | AcueductoNuevo y Responsable |
| 4 | 1.1.6, 1.2.1 | Backend Dev | Relaciones y mapeo referencias |
| 5 | 1.2.2, 1.2.3, 1.2.4, 1.2.5 | Full Team | Análisis completo de impacto |

---

## 🚨 **Riesgos y Mitigaciones**

### **Riesgo 1: Complejidad de relaciones**
- **Probabilidad**: Media
- **Impacto**: Alto
- **Mitigación**: Tests exhaustivos de relaciones, validación con DBA

### **Riesgo 2: Pérdida de datos en migración**
- **Probabilidad**: Baja
- **Impacto**: Crítico
- **Mitigación**: Backup completo, tests de migración, rollback plan

### **Riesgo 3: Impacto en rendimiento**
- **Probabilidad**: Media
- **Impacto**: Medio
- **Mitigación**: Análisis de queries, índices optimizados, profiling

---

## 📞 **Contactos y Responsabilidades**

- **Backend Lead**: Responsable de modelos y migraciones
- **Frontend Lead**: Análisis de impacto en UI
- **DBA**: Revisión de estructura y rendimiento
- **QA**: Validación de tests y criterios de aceptación
- **Business Analyst**: Validación de requerimientos organizacionales

---

**Al completar esta fase, tendremos la base sólida para implementar la nueva estructura organizacional de Hidroven manteniendo la integridad y funcionalidad del sistema existente.**