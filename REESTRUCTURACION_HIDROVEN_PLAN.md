# 🏢 Plan de Reestructuración Organizacional - Hidroven

## 📋 Análisis de la Situación Actual vs Nueva Estructura

### 🔍 **Estructura Actual (Según imagen y código)**
```
OrganizacionCentral (parent/child hierarchy)
├── Sucursal
    └── Acueducto
```

### 🎯 **Nueva Estructura Requerida - Hidroven**
```
HIDROVEN (Empresa Principal)
├── Vicepresidencia de Comercialización
├── Vicepresidencia de Operaciones Hídricas  
│   ├── Almacén Regional Zulia (ZUL)
│   ├── Almacén Regional Carabobo (CAR)
│   ├── Almacén Regional Miranda (MIR)
│   ├── Almacén Regional Aragua (ARA)
│   ├── Almacén Regional Lara (LAR)
│   ├── Almacén Regional Táchira (TAC)
│   ├── Almacén Regional Bolívar (BOL)
│   ├── Almacén Regional Anzoátegui (ANZ)
│   └── Almacén Regional Monagas (MON)
└── Vicepresidencia Administrativa
    └── [Cada VP tiene sus propias unidades operativas]
        └── [Acueductos y sistemas de agua]
```

### 📊 **Sistema de Trazabilidad de Activos**
```
Código Único Evolutivo:
ZUL-BOMBA-000001-2024 → CAR-ZUL-BOMBA-000001-2024 → MIR-CAR-ZUL-BOMBA-000001-2024

Estados del Activo:
EN_ALMACEN → EN_TRANSITO → INSTALADO → EN_USO → MANTENIMIENTO

Flujo de Aprobación:
Solicitud → Aprobación Origen → Aprobación Destino → Ejecución → Confirmación
```

### 📊 **Jerarquía Organizacional Detallada**
```
Nivel 1: EMPRESA
└── Hidroven (Presidente - Máxima Autoridad)

Nivel 2: VICEPRESIDENCIAS
├── VP Comercialización (Responsable VP)
├── VP Operaciones Hídricas (Responsable VP)
└── VP Administrativa (Responsable VP)

Nivel 3: DIRECCIONES/GERENCIAS
├── [Bajo cada VP]
    ├── Direcciones Regionales
    ├── Gerencias Operativas
    └── Unidades Especializadas

Nivel 4: UNIDADES OPERATIVAS
└── Acueductos, Plantas, Sistemas
```

## 🎯 **Objetivos de la Reestructuración**

1. **Mantener Lógica de Negocio**: Preservar funcionalidad actual del inventario
2. **Implementar Jerarquía Real**: Reflejar estructura organizacional de Hidroven
3. **Escalabilidad**: Permitir crecimiento y nuevas unidades
4. **Trazabilidad**: Mantener auditoría y permisos por nivel
5. **Compatibilidad**: Migración sin pérdida de datos

---

## 📋 **PLAN DE TAREAS COMPLEJAS**

### 🔧 **FASE 1: Análisis y Diseño de Modelos**

#### **Tarea 1.1: Diseño del Nuevo Modelo Organizacional**
**Complejidad**: Alta  
**Tiempo Estimado**: 3-4 días  
**Dependencias**: Ninguna

**Subtareas**:
- [ ] 1.1.1 Crear modelo `Empresa` (Hidroven)
- [ ] 1.1.2 Crear modelo `Vicepresidencia` con tipos específicos
- [ ] 1.1.3 Crear modelo `UnidadOrganizacional` (genérico para direcciones/gerencias)
- [ ] 1.1.4 Rediseñar modelo `Acueducto` para nueva jerarquía
- [ ] 1.1.5 Crear modelo `Responsable` para asignación de autoridades
- [ ] 1.1.6 Definir relaciones y constraints de integridad

**Entregables**:
- Nuevos modelos Django
- Diagrama ER actualizado
- Documentación de relaciones

#### **Tarea 1.2: Análisis de Impacto en Sistema Existente**
**Complejidad**: Media  
**Tiempo Estimado**: 2 días  
**Dependencias**: 1.1

**Subtareas**:
- [ ] 1.2.1 Mapear todas las referencias a `OrganizacionCentral`
- [ ] 1.2.2 Identificar queries que necesitan actualización
- [ ] 1.2.3 Analizar impacto en permisos y filtros
- [ ] 1.2.4 Revisar serializers y ViewSets afectados
- [ ] 1.2.5 Documentar cambios necesarios en frontend

**Entregables**:
- Reporte de impacto
- Lista de archivos a modificar
- Plan de migración de datos

---

### 🏗️ **FASE 2: Implementación de Backend**

#### **Tarea 2.1: Implementación de Nuevos Modelos**
**Complejidad**: Alta  
**Tiempo Estimado**: 4-5 días  
**Dependencias**: 1.1, 1.2

**Subtareas**:
- [ ] 2.1.1 Implementar modelo `Empresa`
  ```python
  class Empresa(models.Model):
      nombre = models.CharField(max_length=200, unique=True)
      rif = models.CharField(max_length=30, unique=True)
      presidente = models.ForeignKey(User, on_delete=models.PROTECT)
      # Campos adicionales
  ```

- [ ] 2.1.2 Implementar modelo `Vicepresidencia`
  ```python
  class Vicepresidencia(models.Model):
      class TipoVP(models.TextChoices):
          COMERCIALIZACION = 'COMERCIALIZACION', 'Comercialización'
          OPERACIONES = 'OPERACIONES', 'Operaciones Hídricas'
          ADMINISTRATIVA = 'ADMINISTRATIVA', 'Administrativa'
      
      empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
      tipo = models.CharField(max_length=20, choices=TipoVP.choices)
      responsable = models.ForeignKey(User, on_delete=models.PROTECT)
  ```

- [ ] 2.1.3 Implementar modelo `UnidadOrganizacional`
- [ ] 2.1.4 Actualizar modelo `Acueducto` con nueva jerarquía
- [ ] 2.1.5 Crear migraciones Django
- [ ] 2.1.6 Implementar validaciones y constraints

**Entregables**:
- Modelos implementados
- Migraciones creadas
- Tests unitarios básicos

#### **Tarea 2.2: Actualización de Serializers y ViewSets**
**Complejidad**: Media-Alta  
**Tiempo Estimado**: 3 días  
**Dependencias**: 2.1

**Subtareas**:
- [ ] 2.2.1 Crear serializers para nuevos modelos
- [ ] 2.2.2 Actualizar serializers existentes
- [ ] 2.2.3 Modificar ViewSets con nueva lógica de filtrado
- [ ] 2.2.4 Actualizar permisos por jerarquía organizacional
- [ ] 2.2.5 Implementar endpoints para gestión organizacional

**Entregables**:
- Serializers actualizados
- ViewSets modificados
- Documentación API actualizada

#### **Tarea 2.3: Migración de Datos Existentes**
**Complejidad**: Alta  
**Tiempo Estimado**: 3-4 días  
**Dependencias**: 2.1, 2.2

**Subtareas**:
- [ ] 2.3.1 Crear script de migración de datos
- [ ] 2.3.2 Mapear `OrganizacionCentral` existentes a nueva estructura
- [ ] 2.3.3 Crear registros de Hidroven y Vicepresidencias
- [ ] 2.3.4 Reasignar Acueductos a nueva jerarquía
- [ ] 2.3.5 Validar integridad de datos migrados
- [ ] 2.3.6 Crear rollback plan

**Entregables**:
- Script de migración
- Datos migrados y validados
- Plan de rollback

---

### 🎨 **FASE 3: Actualización de Frontend**

#### **Tarea 3.1: Actualización de Servicios API**
**Complejidad**: Media  
**Tiempo Estimado**: 2 días  
**Dependencias**: 2.2

**Subtareas**:
- [ ] 3.1.1 Actualizar `inventory.service.js` con nuevos endpoints
- [ ] 3.1.2 Crear servicios para gestión organizacional
- [ ] 3.1.3 Actualizar llamadas API existentes
- [ ] 3.1.4 Implementar manejo de errores para nueva estructura

**Entregables**:
- Servicios API actualizados
- Nuevos servicios organizacionales

#### **Tarea 3.2: Actualización de Componentes de Administración**
**Complejidad**: Media-Alta  
**Tiempo Estimado**: 4 días  
**Dependencias**: 3.1

**Subtareas**:
- [ ] 3.2.1 Actualizar página `Administracion.jsx`
- [ ] 3.2.2 Crear componente de gestión de Vicepresidencias
- [ ] 3.2.3 Actualizar formularios de Acueductos
- [ ] 3.2.4 Implementar selector jerárquico de organización
- [ ] 3.2.5 Actualizar filtros y búsquedas

**Entregables**:
- Componentes actualizados
- Nueva interfaz organizacional

#### **Tarea 3.3: Actualización de Dashboard y Reportes**
**Complejidad**: Media  
**Tiempo Estimado**: 2-3 días  
**Dependencias**: 3.1, 3.2

**Subtareas**:
- [ ] 3.3.1 Actualizar métricas del Dashboard por VP
- [ ] 3.3.2 Modificar reportes para nueva jerarquía
- [ ] 3.3.3 Actualizar filtros organizacionales
- [ ] 3.3.4 Implementar vistas por Vicepresidencia

**Entregables**:
- Dashboard actualizado
- Reportes con nueva estructura

---

### 🔐 **FASE 4: Seguridad y Permisos**

#### **Tarea 4.1: Actualización del Sistema de Permisos**
**Complejidad**: Alta  
**Tiempo Estimado**: 3-4 días  
**Dependencias**: 2.1, 2.2

**Subtareas**:
- [ ] 4.1.1 Definir roles por nivel organizacional
- [ ] 4.1.2 Implementar permisos jerárquicos
- [ ] 4.1.3 Actualizar middleware de permisos
- [ ] 4.1.4 Crear grupos de usuarios por VP
- [ ] 4.1.5 Implementar filtrado automático por jerarquía

**Entregables**:
- Sistema de permisos actualizado
- Roles y grupos configurados

#### **Tarea 4.2: Migración de Usuarios y Permisos**
**Complejidad**: Media  
**Tiempo Estimado**: 2 días  
**Dependencias**: 4.1

**Subtareas**:
- [ ] 4.2.1 Mapear usuarios existentes a nueva estructura
- [ ] 4.2.2 Asignar usuarios a Vicepresidencias
- [ ] 4.2.3 Configurar permisos por defecto
- [ ] 4.2.4 Validar accesos y restricciones

**Entregables**:
- Usuarios migrados
- Permisos configurados

---

### 🧪 **FASE 5: Testing y Validación**

#### **Tarea 5.1: Testing Integral del Sistema**
**Complejidad**: Alta  
**Tiempo Estimado**: 4-5 días  
**Dependencias**: Todas las anteriores

**Subtareas**:
- [ ] 5.1.1 Tests unitarios de nuevos modelos
- [ ] 5.1.2 Tests de integración API
- [ ] 5.1.3 Tests de migración de datos
- [ ] 5.1.4 Tests de permisos y seguridad
- [ ] 5.1.5 Tests end-to-end del frontend
- [ ] 5.1.6 Tests de rendimiento

**Entregables**:
- Suite de tests completa
- Reporte de cobertura
- Validación de funcionalidad

#### **Tarea 5.2: Validación con Usuarios**
**Complejidad**: Media  
**Tiempo Estimado**: 2-3 días  
**Dependencias**: 5.1

**Subtareas**:
- [ ] 5.2.1 Preparar ambiente de testing
- [ ] 5.2.2 Capacitar usuarios clave
- [ ] 5.2.3 Ejecutar casos de uso críticos
- [ ] 5.2.4 Recopilar feedback
- [ ] 5.2.5 Implementar ajustes necesarios

**Entregables**:
- Validación de usuarios
- Ajustes implementados

---

### 🚀 **FASE 6: Deployment y Documentación**

#### **Tarea 6.1: Preparación para Producción**
**Complejidad**: Media  
**Tiempo Estimado**: 2 días  
**Dependencias**: 5.2

**Subtareas**:
- [ ] 6.1.1 Actualizar configuraciones de producción
- [ ] 6.1.2 Preparar scripts de deployment
- [ ] 6.1.3 Configurar backup pre-migración
- [ ] 6.1.4 Preparar plan de rollback
- [ ] 6.1.5 Documentar proceso de deployment

**Entregables**:
- Configuración de producción
- Scripts de deployment
- Plan de contingencia

#### **Tarea 6.2: Documentación y Capacitación**
**Complejidad**: Media  
**Tiempo Estimado**: 3 días  
**Dependencias**: 6.1

**Subtareas**:
- [ ] 6.2.1 Actualizar documentación técnica
- [ ] 6.2.2 Crear manual de usuario actualizado
- [ ] 6.2.3 Documentar nueva estructura organizacional
- [ ] 6.2.4 Preparar material de capacitación
- [ ] 6.2.5 Crear guías de administración

**Entregables**:
- Documentación completa
- Material de capacitación

---

## 📊 **Resumen del Plan**

### **Cronograma Estimado**
- **Fase 1**: 5-6 días (Análisis y Diseño)
- **Fase 2**: 10-12 días (Backend)
- **Fase 3**: 8-9 días (Frontend)
- **Fase 4**: 5-6 días (Seguridad)
- **Fase 5**: 6-8 días (Testing)
- **Fase 6**: 5 días (Deployment)

**Total Estimado**: 39-46 días laborales (~8-9 semanas)

### **Recursos Necesarios**
- **Backend Developer**: Full-time
- **Frontend Developer**: Full-time
- **DBA/DevOps**: Part-time (migraciones y deployment)
- **QA Tester**: Part-time (testing y validación)
- **Business Analyst**: Part-time (validación de requerimientos)

### **Riesgos Identificados**
1. **Complejidad de migración de datos**: Mitigación con testing exhaustivo
2. **Impacto en usuarios**: Mitigación con capacitación y rollback plan
3. **Pérdida de funcionalidad**: Mitigación con tests de regresión
4. **Problemas de rendimiento**: Mitigación con optimización de queries

### **Criterios de Éxito**
- ✅ Migración completa sin pérdida de datos
- ✅ Funcionalidad existente preservada
- ✅ Nueva estructura organizacional implementada
- ✅ Usuarios capacitados y satisfechos
- ✅ Sistema estable en producción

---

**Este plan mantiene la lógica de negocio actual mientras implementa la nueva estructura organizacional de Hidroven de manera sistemática y controlada.**