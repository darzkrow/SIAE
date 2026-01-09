# 🔧 MÓDULO DE ADMINISTRACIÓN

## 📋 Resumen

El módulo de Administración permite a los administradores gestionar todos los datos maestros del sistema:
- **Sucursales**: Crear y gestionar sucursales
- **Acueductos**: Crear y gestionar acueductos (hidrológicas)
- **Tuberías**: Crear y gestionar inventario de tuberías
- **Equipos**: Crear y gestionar inventario de equipos

## 🎯 Acceso

**Ubicación**: `frontend/src/pages/Administracion.jsx`
**Ruta**: `/administracion`
**Permisos**: Solo ADMIN
**Menú**: Sidebar → Administración (solo visible para ADMIN)

## 📊 Funcionalidades

### 1. Gestión de Sucursales

**Crear Sucursal**:
- Nombre (único)
- Organización Central (seleccionar de lista)

**Editar Sucursal**:
- Modificar nombre
- Cambiar organización central

**Eliminar Sucursal**:
- Eliminar sucursal (con confirmación)

**Endpoints**:
- `GET /api/sucursales/` - Listar sucursales
- `POST /api/sucursales/` - Crear sucursal
- `PUT /api/sucursales/{id}/` - Actualizar sucursal
- `DELETE /api/sucursales/{id}/` - Eliminar sucursal

### 2. Gestión de Acueductos

**Crear Acueducto**:
- Nombre
- Sucursal (seleccionar de lista)

**Editar Acueducto**:
- Modificar nombre
- Cambiar sucursal

**Eliminar Acueducto**:
- Eliminar acueducto (con confirmación)

**Endpoints**:
- `GET /api/acueductos/` - Listar acueductos
- `POST /api/acueductos/` - Crear acueducto
- `PUT /api/acueductos/{id}/` - Actualizar acueducto
- `DELETE /api/acueductos/{id}/` - Eliminar acueducto

### 3. Gestión de Tuberías

**Crear Tubería**:
- Nombre
- Categoría (seleccionar de lista)
- Material (PVC, Hierro Dúctil, Cemento, Otro)
- Tipo de Uso (Aguas Potables, Aguas Servidas, Riego)
- Diámetro Nominal (mm)
- Longitud (m)
- Descripción (opcional)

**Editar Tubería**:
- Modificar todos los campos

**Eliminar Tubería**:
- Eliminar tubería (con confirmación)

**Endpoints**:
- `GET /api/tuberias/` - Listar tuberías
- `POST /api/tuberias/` - Crear tubería
- `PUT /api/tuberias/{id}/` - Actualizar tubería
- `DELETE /api/tuberias/{id}/` - Eliminar tubería

### 4. Gestión de Equipos

**Crear Equipo**:
- Nombre
- Categoría (seleccionar de lista)
- Marca (opcional)
- Modelo (opcional)
- Potencia (HP) (opcional)
- Número de Serie (único)
- Descripción (opcional)

**Editar Equipo**:
- Modificar todos los campos

**Eliminar Equipo**:
- Eliminar equipo (con confirmación)

**Endpoints**:
- `GET /api/equipos/` - Listar equipos
- `POST /api/equipos/` - Crear equipo
- `PUT /api/equipos/{id}/` - Actualizar equipo
- `DELETE /api/equipos/{id}/` - Eliminar equipo

## 🎨 Interfaz

### Estructura

```
┌─────────────────────────────────────────────────────────┐
│ Administración                              [+ Nuevo]    │
├─────────────────────────────────────────────────────────┤
│ [Sucursales] [Acueductos] [Tuberías] [Equipos]         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Formulario (si está abierto)                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Crear Nuevo [Sucursal/Acueducto/Tubería/Equipo] │   │
│  │                                                  │   │
│  │ Campo 1: [_________________]                    │   │
│  │ Campo 2: [_________________]                    │   │
│  │                                                  │   │
│  │ [Crear] [Cancelar]                              │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  Tabla de Datos                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Columna1 | Columna2 | Columna3 | Acciones      │   │
│  ├──────────────────────────────────────────────────┤   │
│  │ Dato1    | Dato2    | Dato3    | [✏️] [🗑️]      │   │
│  │ Dato1    | Dato2    | Dato3    | [✏️] [🗑️]      │   │
│  │ Dato1    | Dato2    | Dato3    | [✏️] [🗑️]      │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Tabs

- **Sucursales**: Gestión de sucursales
- **Acueductos**: Gestión de acueductos (hidrológicas)
- **Tuberías**: Gestión de tuberías
- **Equipos**: Gestión de equipos

### Botones

- **[+ Nuevo]**: Abre el formulario para crear un nuevo elemento
- **[✏️]**: Edita el elemento seleccionado
- **[🗑️]**: Elimina el elemento seleccionado (con confirmación)
- **[Crear/Actualizar]**: Guarda los cambios
- **[Cancelar]**: Cierra el formulario

## 📝 Flujo de Trabajo

### Crear un Elemento

1. Hacer clic en **[+ Nuevo]**
2. Se abre el formulario
3. Completar los campos requeridos (marcados con *)
4. Hacer clic en **[Crear]**
5. Se muestra mensaje de éxito
6. Se actualiza la tabla

### Editar un Elemento

1. Hacer clic en **[✏️]** en la fila del elemento
2. Se abre el formulario con los datos precargados
3. Modificar los campos necesarios
4. Hacer clic en **[Actualizar]**
5. Se muestra mensaje de éxito
6. Se actualiza la tabla

### Eliminar un Elemento

1. Hacer clic en **[🗑️]** en la fila del elemento
2. Se muestra confirmación
3. Confirmar eliminación
4. Se muestra mensaje de éxito
5. Se actualiza la tabla

## 🔐 Permisos

| Acción | ADMIN | OPERADOR |
|--------|-------|----------|
| Ver datos | ✅ | ❌ |
| Crear | ✅ | ❌ |
| Editar | ✅ | ❌ |
| Eliminar | ✅ | ❌ |

## 📊 Datos Maestros

### Sucursales

Representa las sucursales de la organización.

**Campos**:
- `id`: ID único
- `nombre`: Nombre de la sucursal (único)
- `organizacion_central`: Referencia a OrganizacionCentral

**Ejemplo**:
```json
{
  "id": 1,
  "nombre": "Sucursal Central",
  "organizacion_central": 1
}
```

### Acueductos

Representa los acueductos (hidrológicas) dentro de una sucursal.

**Campos**:
- `id`: ID único
- `nombre`: Nombre del acueducto
- `sucursal`: Referencia a Sucursal

**Ejemplo**:
```json
{
  "id": 1,
  "nombre": "Acueducto Los Andes",
  "sucursal": 1
}
```

### Tuberías

Representa el inventario de tuberías.

**Campos**:
- `id`: ID único
- `nombre`: Nombre de la tubería
- `descripcion`: Descripción (opcional)
- `categoria`: Referencia a Categoría
- `material`: Material (PVC, HIERRO, CEMENTO, OTRO)
- `tipo_uso`: Tipo de uso (POTABLE, SERVIDAS, RIEGO)
- `diametro_nominal_mm`: Diámetro en mm
- `longitud_m`: Longitud en metros

**Ejemplo**:
```json
{
  "id": 1,
  "nombre": "Tubería PVC 50mm",
  "descripcion": "Tubería de PVC para agua potable",
  "categoria": 1,
  "material": "PVC",
  "tipo_uso": "POTABLE",
  "diametro_nominal_mm": 50,
  "longitud_m": 100.00
}
```

### Equipos

Representa el inventario de equipos.

**Campos**:
- `id`: ID único
- `nombre`: Nombre del equipo
- `descripcion`: Descripción (opcional)
- `categoria`: Referencia a Categoría
- `marca`: Marca (opcional)
- `modelo`: Modelo (opcional)
- `potencia_hp`: Potencia en HP (opcional)
- `numero_serie`: Número de serie (único)

**Ejemplo**:
```json
{
  "id": 1,
  "nombre": "Bomba Centrífuga",
  "descripcion": "Bomba para agua potable",
  "categoria": 1,
  "marca": "Grundfos",
  "modelo": "CR 32-160",
  "potencia_hp": 5.5,
  "numero_serie": "GR-2024-001"
}
```

## 🚀 Casos de Uso

### Caso 1: Crear una Nueva Sucursal

1. Ir a Administración → Sucursales
2. Hacer clic en [+ Nuevo]
3. Ingresar nombre: "Sucursal Occidente"
4. Seleccionar organización: "GSIH"
5. Hacer clic en [Crear Sucursal]
6. Sucursal creada exitosamente

### Caso 2: Agregar un Acueducto

1. Ir a Administración → Acueductos
2. Hacer clic en [+ Nuevo]
3. Ingresar nombre: "Acueducto Metropolitano"
4. Seleccionar sucursal: "Sucursal Central"
5. Hacer clic en [Crear Acueducto]
6. Acueducto creado exitosamente

### Caso 3: Cargar Inventario de Tuberías

1. Ir a Administración → Tuberías
2. Hacer clic en [+ Nuevo]
3. Ingresar datos:
   - Nombre: "Tubería PVC 75mm"
   - Categoría: "Tuberías"
   - Material: "PVC"
   - Tipo de Uso: "Aguas Potables"
   - Diámetro: 75
   - Longitud: 500
4. Hacer clic en [Crear Tubería]
5. Tubería agregada al inventario

### Caso 4: Cargar Inventario de Equipos

1. Ir a Administración → Equipos
2. Hacer clic en [+ Nuevo]
3. Ingresar datos:
   - Nombre: "Bomba Sumergible"
   - Categoría: "Bombas"
   - Marca: "Pedrollo"
   - Modelo: "4SR"
   - Potencia: 1.5
   - Número de Serie: "PED-2024-001"
4. Hacer clic en [Crear Equipo]
5. Equipo agregado al inventario

## 🔄 Integración con Otros Módulos

### Movimientos
Los artículos creados en Administración se pueden usar en:
- Módulo de Movimientos (crear movimientos de inventario)
- Módulo de Stock (ver stock disponible)

### Alertas
Los acueductos creados en Administración se pueden usar en:
- Módulo de Alertas (crear alertas de stock bajo)

### Reportes
Los datos creados en Administración se usan en:
- Módulo de Reportes (generar reportes)

## 📈 Estadísticas

**Líneas de código**: ~600
**Componentes**: 1 (Administracion.jsx)
**Endpoints**: 16 (4 por cada entidad)
**Funcionalidades**: CRUD completo para 4 entidades

## 🛠️ Tecnologías

- React (hooks, state management)
- Axios (HTTP requests)
- Tailwind CSS (styling)
- Lucide React (icons)

## 📝 Validaciones

### Sucursales
- Nombre: Requerido, único
- Organización: Requerida

### Acueductos
- Nombre: Requerido
- Sucursal: Requerida

### Tuberías
- Nombre: Requerido
- Categoría: Requerida
- Material: Requerido
- Tipo de Uso: Requerido
- Diámetro: Requerido, número
- Longitud: Requerida, número positivo

### Equipos
- Nombre: Requerido
- Categoría: Requerida
- Número de Serie: Requerido, único
- Potencia: Opcional, número

## 🎓 Conclusión

El módulo de Administración proporciona una interfaz completa y fácil de usar para gestionar todos los datos maestros del sistema GSIH. Permite a los administradores:

✅ Crear y gestionar sucursales
✅ Crear y gestionar acueductos (hidrológicas)
✅ Cargar inventario de tuberías
✅ Cargar inventario de equipos
✅ Editar y eliminar datos
✅ Validar datos antes de guardar

---

**Fecha**: Enero 8, 2026
**Versión**: 1.0
**Estado**: Completado
**Próximas Mejoras**: Importación masiva de datos (CSV/Excel)
