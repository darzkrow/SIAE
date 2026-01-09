# Endpoints de Búsqueda de Stock - Documentación

**Fecha**: 8 de Enero de 2026  
**Status**: ✅ IMPLEMENTADO

---

## 📋 Resumen

Se han mejorado y ampliado los endpoints de búsqueda de stock con validaciones adicionales y un nuevo endpoint de búsqueda avanzada.

---

## 🔍 Endpoint 1: `stock_search` (Mejorado)

### URL
```
GET /api/reportes/stock_search/
```

### Descripción
Búsqueda de stock de un artículo específico por ubicación con validaciones completas.

### Parámetros

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `articulo_id` | integer | ✅ Sí | ID del artículo (tubería o equipo) |
| `tipo` | string | ✅ Sí | Tipo de artículo: `tuberia` o `equipo` |
| `sucursal_id` | integer | ❌ No | Filtrar por sucursal específica |

### Validaciones Implementadas

1. **Parámetros Requeridos**
   - `articulo_id` y `tipo` son obligatorios
   - Error 400 si faltan

2. **Tipo de Artículo Válido**
   - Solo acepta `tuberia` o `equipo`
   - Error 400 si es inválido

3. **ID Numérico**
   - `articulo_id` debe ser un número entero
   - Error 400 si no es válido

4. **Sucursal Válida**
   - Si se proporciona `sucursal_id`, debe existir
   - Error 404 si no existe

5. **Stock Disponible**
   - Verifica que hay stock para el artículo
   - Retorna mensaje si no hay stock

### Ejemplos de Uso

#### Búsqueda de Tubería
```bash
curl "http://localhost:8000/api/reportes/stock_search/?articulo_id=1&tipo=tuberia"
```

#### Búsqueda de Equipo en Sucursal Específica
```bash
curl "http://localhost:8000/api/reportes/stock_search/?articulo_id=5&tipo=equipo&sucursal_id=2"
```

### Respuesta Exitosa (200)

```json
{
  "articulo_id": 1,
  "articulo": "Tubería PVC 2 pulgadas",
  "tipo": "tuberia",
  "total_ubicaciones": 3,
  "stock_total": 150,
  "sucursal_filtrada": null,
  "resultados": [
    {
      "id": 10,
      "articulo": "Tubería PVC 2 pulgadas",
      "articulo_id": 1,
      "tipo": "tuberia",
      "acueducto": "Sistema Principal",
      "acueducto_id": 1,
      "sucursal": "Planta A",
      "sucursal_id": 1,
      "cantidad": 50,
      "fecha_actualizacion": "2026-01-08T10:30:00Z",
      "estado": "normal"
    },
    {
      "id": 11,
      "articulo": "Tubería PVC 2 pulgadas",
      "articulo_id": 1,
      "tipo": "tuberia",
      "acueducto": "Sistema Secundario",
      "acueducto_id": 2,
      "sucursal": "Planta A",
      "sucursal_id": 1,
      "cantidad": 75,
      "fecha_actualizacion": "2026-01-08T10:30:00Z",
      "estado": "normal"
    },
    {
      "id": 12,
      "articulo": "Tubería PVC 2 pulgadas",
      "articulo_id": 1,
      "tipo": "tuberia",
      "acueducto": "Sistema Terciario",
      "acueducto_id": 3,
      "sucursal": "Planta B",
      "sucursal_id": 2,
      "cantidad": 25,
      "fecha_actualizacion": "2026-01-08T10:30:00Z",
      "estado": "bajo"
    }
  ]
}
```

### Respuestas de Error

#### Error 400 - Parámetros Faltantes
```json
{
  "error": "Se requieren parámetros: articulo_id y tipo"
}
```

#### Error 400 - Tipo Inválido
```json
{
  "error": "Tipo de artículo inválido. Debe ser \"tuberia\" o \"equipo\""
}
```

#### Error 400 - ID No Numérico
```json
{
  "error": "articulo_id debe ser un número válido"
}
```

#### Error 404 - Artículo No Encontrado
```json
{
  "error": "Tubería con ID 999 no encontrada"
}
```

#### Error 404 - Sucursal No Encontrada
```json
{
  "error": "Sucursal con ID 999 no encontrada"
}
```

#### Sin Stock Disponible (200)
```json
{
  "articulo_id": 1,
  "tipo": "tuberia",
  "total_ubicaciones": 0,
  "stock_total": 0,
  "mensaje": "No hay stock disponible para este artículo",
  "resultados": []
}
```

---

## 🔎 Endpoint 2: `stock_search_advanced` (Nuevo)

### URL
```
GET /api/reportes/stock_search_advanced/
```

### Descripción
Búsqueda avanzada de stock con múltiples filtros y búsqueda por nombre.

### Parámetros

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `nombre` | string | ❌ No | Buscar por nombre del artículo (búsqueda parcial) |
| `sucursal_id` | integer | ❌ No | Filtrar por sucursal |
| `acueducto_id` | integer | ❌ No | Filtrar por acueducto específico |
| `tipo` | string | ❌ No | Tipo: `tuberia`, `equipo` o `all` (default: `all`) |
| `stock_bajo` | boolean | ❌ No | Mostrar solo artículos con stock ≤ 10 (default: `false`) |

### Validaciones Implementadas

1. **Al Menos Un Filtro**
   - Se requiere al menos: `nombre`, `sucursal_id` o `acueducto_id`
   - Error 400 si no hay filtros

2. **IDs Numéricos**
   - `sucursal_id` y `acueducto_id` deben ser números
   - Error 400 si no son válidos

3. **Búsqueda Case-Insensitive**
   - La búsqueda por nombre ignora mayúsculas/minúsculas
   - Busca en nombre y descripción

4. **Ordenamiento Automático**
   - Si `stock_bajo=true`, ordena por cantidad (menor primero)

### Ejemplos de Uso

#### Búsqueda por Nombre
```bash
curl "http://localhost:8000/api/reportes/stock_search_advanced/?nombre=tuberia"
```

#### Búsqueda por Sucursal
```bash
curl "http://localhost:8000/api/reportes/stock_search_advanced/?sucursal_id=1"
```

#### Búsqueda de Stock Bajo en Sucursal
```bash
curl "http://localhost:8000/api/reportes/stock_search_advanced/?sucursal_id=1&stock_bajo=true"
```

#### Búsqueda Combinada
```bash
curl "http://localhost:8000/api/reportes/stock_search_advanced/?nombre=motor&tipo=equipo&stock_bajo=true"
```

#### Búsqueda en Acueducto Específico
```bash
curl "http://localhost:8000/api/reportes/stock_search_advanced/?acueducto_id=3&tipo=all"
```

### Respuesta Exitosa (200)

```json
{
  "filtros": {
    "nombre": "motor",
    "sucursal_id": null,
    "acueducto_id": null,
    "tipo": "equipo",
    "stock_bajo": true
  },
  "total_resultados": 2,
  "stock_total": 8,
  "resultados": [
    {
      "id": 25,
      "articulo": "Motor de Bombeo 5HP",
      "articulo_id": 5,
      "tipo": "equipo",
      "acueducto": "Sistema Principal",
      "acueducto_id": 1,
      "sucursal": "Planta A",
      "sucursal_id": 1,
      "cantidad": 3,
      "fecha_actualizacion": "2026-01-08T10:30:00Z",
      "estado": "bajo"
    },
    {
      "id": 26,
      "articulo": "Motor de Bombeo 10HP",
      "articulo_id": 6,
      "tipo": "equipo",
      "acueducto": "Sistema Secundario",
      "acueducto_id": 2,
      "sucursal": "Planta A",
      "sucursal_id": 1,
      "cantidad": 5,
      "fecha_actualizacion": "2026-01-08T10:30:00Z",
      "estado": "bajo"
    }
  ]
}
```

### Respuestas de Error

#### Error 400 - Sin Filtros
```json
{
  "error": "Se requiere al menos uno de: nombre, sucursal_id o acueducto_id"
}
```

#### Error 400 - ID No Numérico
```json
{
  "error": "sucursal_id debe ser numérico"
}
```

#### Sin Resultados (200)
```json
{
  "filtros": {
    "nombre": "inexistente",
    "sucursal_id": null,
    "acueducto_id": null,
    "tipo": "all",
    "stock_bajo": false
  },
  "total_resultados": 0,
  "stock_total": 0,
  "resultados": []
}
```

---

## 📊 Campos de Respuesta

### Información del Artículo
- `articulo`: Nombre del artículo
- `articulo_id`: ID del artículo
- `tipo`: Tipo (tuberia/equipo)

### Ubicación
- `acueducto`: Nombre del acueducto
- `acueducto_id`: ID del acueducto
- `sucursal`: Nombre de la sucursal
- `sucursal_id`: ID de la sucursal

### Stock
- `cantidad`: Cantidad disponible
- `estado`: `normal` o `bajo` (≤ 10 unidades)
- `fecha_actualizacion`: Última actualización

---

## 🎯 Casos de Uso

### 1. Verificar Stock de Artículo Específico
```bash
# Buscar todas las ubicaciones de una tubería
curl "http://localhost:8000/api/reportes/stock_search/?articulo_id=1&tipo=tuberia"
```

### 2. Buscar Stock en Sucursal Específica
```bash
# Buscar todas las tuberías en la Planta A
curl "http://localhost:8000/api/reportes/stock_search_advanced/?sucursal_id=1&tipo=tuberia"
```

### 3. Encontrar Artículos con Stock Bajo
```bash
# Buscar todos los artículos con stock bajo
curl "http://localhost:8000/api/reportes/stock_search_advanced/?stock_bajo=true"
```

### 4. Buscar por Nombre
```bash
# Buscar todos los motores
curl "http://localhost:8000/api/reportes/stock_search_advanced/?nombre=motor"
```

### 5. Búsqueda Compleja
```bash
# Buscar motores con stock bajo en la Planta A
curl "http://localhost:8000/api/reportes/stock_search_advanced/?nombre=motor&sucursal_id=1&stock_bajo=true"
```

---

## 🔐 Seguridad

- ✅ Validación de entrada en todos los parámetros
- ✅ Manejo de errores descriptivos
- ✅ Prevención de inyección SQL (ORM)
- ✅ Respuestas consistentes

---

## 📈 Mejoras Implementadas

1. **Validaciones Completas**
   - Verificación de tipos de datos
   - Validación de existencia de registros
   - Mensajes de error descriptivos

2. **Información Enriquecida**
   - IDs de artículos y ubicaciones
   - Estado del stock (normal/bajo)
   - Fecha de última actualización

3. **Búsqueda Avanzada**
   - Búsqueda por nombre (case-insensitive)
   - Múltiples filtros combinables
   - Ordenamiento automático

4. **Respuestas Consistentes**
   - Estructura uniforme
   - Información de filtros aplicados
   - Totales y resúmenes

---

## 🧪 Pruebas

### Test 1: Búsqueda Exitosa
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search/?articulo_id=1&tipo=tuberia"
```
**Esperado**: 200 OK con resultados

### Test 2: Parámetros Faltantes
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search/"
```
**Esperado**: 400 Bad Request

### Test 3: Tipo Inválido
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search/?articulo_id=1&tipo=invalido"
```
**Esperado**: 400 Bad Request

### Test 4: Búsqueda Avanzada
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search_advanced/?nombre=tuberia&stock_bajo=true"
```
**Esperado**: 200 OK con resultados filtrados

---

## 📝 Notas

- Los endpoints están disponibles en `/api/reportes/`
- Requieren autenticación
- Responden en JSON
- Soportan filtrado por sucursal y acueducto
- El estado "bajo" se define como cantidad ≤ 10

---

**Status**: ✅ COMPLETADO Y FUNCIONAL
