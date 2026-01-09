# Pruebas de Endpoints de Búsqueda - Guía Práctica

**Fecha**: 8 de Enero de 2026  
**Status**: ✅ LISTO PARA PRUEBAS

---

## 🧪 Configuración Inicial

### Requisitos
- Backend corriendo: `python manage.py runserver`
- Datos de prueba cargados: `python manage.py seed_test_data`
- Token de autenticación (si es requerido)

### URL Base
```
http://localhost:8000/api/reportes/
```

---

## 📝 Pruebas del Endpoint `stock_search`

### Test 1: Búsqueda Exitosa de Tubería

**Comando**:
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search/?articulo_id=1&tipo=tuberia"
```

**Esperado**: 
- Status: 200 OK
- Contiene: `total_ubicaciones`, `stock_total`, `resultados`

**Validar**:
- [ ] Respuesta contiene artículo
- [ ] Respuesta contiene ubicaciones
- [ ] Stock total es correcto

---

### Test 2: Búsqueda Exitosa de Equipo

**Comando**:
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search/?articulo_id=1&tipo=equipo"
```

**Esperado**: 
- Status: 200 OK
- Contiene equipos en diferentes ubicaciones

**Validar**:
- [ ] Tipo es "equipo"
- [ ] Contiene información de acueductos
- [ ] Contiene información de sucursales

---

### Test 3: Búsqueda con Filtro de Sucursal

**Comando**:
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search/?articulo_id=1&tipo=tuberia&sucursal_id=1"
```

**Esperado**: 
- Status: 200 OK
- Solo resultados de sucursal 1

**Validar**:
- [ ] Todos los resultados tienen sucursal_id = 1
- [ ] Stock total es menor o igual al sin filtro

---

### Test 4: Error - Parámetros Faltantes

**Comando**:
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search/"
```

**Esperado**: 
- Status: 400 Bad Request
- Mensaje: "Se requieren parámetros: articulo_id y tipo"

**Validar**:
- [ ] Error es descriptivo
- [ ] Status code es 400

---

### Test 5: Error - Tipo Inválido

**Comando**:
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search/?articulo_id=1&tipo=invalido"
```

**Esperado**: 
- Status: 400 Bad Request
- Mensaje: "Tipo de artículo inválido"

**Validar**:
- [ ] Valida tipo correctamente
- [ ] Mensaje es claro

---

### Test 6: Error - ID No Numérico

**Comando**:
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search/?articulo_id=abc&tipo=tuberia"
```

**Esperado**: 
- Status: 400 Bad Request
- Mensaje: "articulo_id debe ser un número válido"

**Validar**:
- [ ] Valida tipo de dato
- [ ] Rechaza strings no numéricos

---

### Test 7: Error - Artículo No Encontrado

**Comando**:
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search/?articulo_id=9999&tipo=tuberia"
```

**Esperado**: 
- Status: 404 Not Found
- Mensaje: "Tubería con ID 9999 no encontrada"

**Validar**:
- [ ] Status code es 404
- [ ] Mensaje es descriptivo

---

### Test 8: Error - Sucursal No Encontrada

**Comando**:
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search/?articulo_id=1&tipo=tuberia&sucursal_id=9999"
```

**Esperado**: 
- Status: 404 Not Found
- Mensaje: "Sucursal con ID 9999 no encontrada"

**Validar**:
- [ ] Valida existencia de sucursal
- [ ] Error es claro

---

### Test 9: Sin Stock Disponible

**Comando**:
```bash
# Primero, crear un artículo sin stock
# Luego buscar
curl -X GET "http://localhost:8000/api/reportes/stock_search/?articulo_id=X&tipo=tuberia"
```

**Esperado**: 
- Status: 200 OK
- Mensaje: "No hay stock disponible para este artículo"
- `total_ubicaciones`: 0
- `stock_total`: 0

**Validar**:
- [ ] Retorna 200 (no error)
- [ ] Mensaje es informativo
- [ ] Resultados vacíos

---

## 📝 Pruebas del Endpoint `stock_search_advanced`

### Test 10: Búsqueda por Nombre

**Comando**:
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search_advanced/?nombre=tuberia"
```

**Esperado**: 
- Status: 200 OK
- Contiene artículos con "tuberia" en nombre

**Validar**:
- [ ] Búsqueda case-insensitive
- [ ] Contiene resultados relevantes
- [ ] Busca en nombre y descripción

---

### Test 11: Búsqueda por Sucursal

**Comando**:
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search_advanced/?sucursal_id=1"
```

**Esperado**: 
- Status: 200 OK
- Todos los resultados de sucursal 1

**Validar**:
- [ ] Todos tienen sucursal_id = 1
- [ ] Contiene tuberías y equipos
- [ ] Total resultados > 0

---

### Test 12: Búsqueda por Acueducto

**Comando**:
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search_advanced/?acueducto_id=1"
```

**Esperado**: 
- Status: 200 OK
- Solo resultados del acueducto 1

**Validar**:
- [ ] Todos tienen acueducto_id = 1
- [ ] Contiene múltiples artículos

---

### Test 13: Búsqueda de Stock Bajo

**Comando**:
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search_advanced/?stock_bajo=true"
```

**Esperado**: 
- Status: 200 OK
- Solo artículos con cantidad ≤ 10

**Validar**:
- [ ] Todos tienen cantidad ≤ 10
- [ ] Ordenados por cantidad (menor primero)
- [ ] Todos tienen estado = "bajo"

---

### Test 14: Búsqueda Combinada

**Comando**:
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search_advanced/?nombre=motor&tipo=equipo&stock_bajo=true"
```

**Esperado**: 
- Status: 200 OK
- Equipos con "motor" en nombre y stock ≤ 10

**Validar**:
- [ ] Todos son equipos
- [ ] Todos tienen "motor" en nombre
- [ ] Todos tienen stock bajo
- [ ] Ordenados por cantidad

---

### Test 15: Búsqueda por Tipo

**Comando**:
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search_advanced/?tipo=tuberia&sucursal_id=1"
```

**Esperado**: 
- Status: 200 OK
- Solo tuberías de sucursal 1

**Validar**:
- [ ] Todos tienen tipo = "tuberia"
- [ ] Todos tienen sucursal_id = 1

---

### Test 16: Error - Sin Filtros

**Comando**:
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search_advanced/"
```

**Esperado**: 
- Status: 400 Bad Request
- Mensaje: "Se requiere al menos uno de: nombre, sucursal_id o acueducto_id"

**Validar**:
- [ ] Valida que hay al menos un filtro
- [ ] Mensaje es claro

---

### Test 17: Error - ID No Numérico

**Comando**:
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search_advanced/?sucursal_id=abc"
```

**Esperado**: 
- Status: 400 Bad Request
- Mensaje: "sucursal_id debe ser numérico"

**Validar**:
- [ ] Valida tipo de dato
- [ ] Rechaza strings

---

### Test 18: Sin Resultados

**Comando**:
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search_advanced/?nombre=inexistente"
```

**Esperado**: 
- Status: 200 OK
- `total_resultados`: 0
- `resultados`: []

**Validar**:
- [ ] Retorna 200 (no error)
- [ ] Resultados vacíos
- [ ] Estructura correcta

---

## 🔍 Pruebas de Validación de Datos

### Test 19: Validar Estructura de Respuesta

**Comando**:
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search/?articulo_id=1&tipo=tuberia" | jq
```

**Validar Campos**:
- [ ] `articulo_id`: número
- [ ] `articulo`: string
- [ ] `tipo`: string (tuberia/equipo)
- [ ] `total_ubicaciones`: número
- [ ] `stock_total`: número
- [ ] `resultados`: array

**Validar Cada Resultado**:
- [ ] `id`: número
- [ ] `articulo`: string
- [ ] `articulo_id`: número
- [ ] `tipo`: string
- [ ] `acueducto`: string
- [ ] `acueducto_id`: número
- [ ] `sucursal`: string
- [ ] `sucursal_id`: número
- [ ] `cantidad`: número
- [ ] `fecha_actualizacion`: timestamp
- [ ] `estado`: string (normal/bajo)

---

### Test 20: Validar Cálculos

**Comando**:
```bash
curl -X GET "http://localhost:8000/api/reportes/stock_search/?articulo_id=1&tipo=tuberia" | jq '.resultados | map(.cantidad) | add'
```

**Validar**:
- [ ] Suma de cantidades = `stock_total`
- [ ] Número de resultados = `total_ubicaciones`

---

## 🧪 Pruebas de Rendimiento

### Test 21: Búsqueda Rápida

**Comando**:
```bash
time curl -X GET "http://localhost:8000/api/reportes/stock_search/?articulo_id=1&tipo=tuberia"
```

**Esperado**: 
- Tiempo < 500ms

**Validar**:
- [ ] Respuesta rápida
- [ ] No hay timeout

---

### Test 22: Búsqueda Avanzada Rápida

**Comando**:
```bash
time curl -X GET "http://localhost:8000/api/reportes/stock_search_advanced/?nombre=tuberia&stock_bajo=true"
```

**Esperado**: 
- Tiempo < 1000ms

**Validar**:
- [ ] Búsqueda rápida
- [ ] Filtros eficientes

---

## 📊 Pruebas de Casos Reales

### Caso 1: Verificar Stock de Artículo Específico
```bash
# Buscar todas las ubicaciones de tubería ID 1
curl -X GET "http://localhost:8000/api/reportes/stock_search/?articulo_id=1&tipo=tuberia"

# Validar:
# - Muestra todas las ubicaciones
# - Stock total es correcto
# - Información de sucursales y acueductos
```

### Caso 2: Encontrar Artículos con Stock Bajo
```bash
# Buscar todos los artículos con stock bajo
curl -X GET "http://localhost:8000/api/reportes/stock_search_advanced/?stock_bajo=true"

# Validar:
# - Solo muestra artículos con cantidad ≤ 10
# - Ordenados por cantidad (menor primero)
# - Útil para alertas
```

### Caso 3: Buscar en Sucursal Específica
```bash
# Buscar todos los motores en Planta A
curl -X GET "http://localhost:8000/api/reportes/stock_search_advanced/?nombre=motor&sucursal_id=1"

# Validar:
# - Solo resultados de sucursal 1
# - Contiene equipos con "motor"
# - Información completa
```

### Caso 4: Búsqueda Compleja
```bash
# Buscar tuberías con stock bajo en acueducto específico
curl -X GET "http://localhost:8000/api/reportes/stock_search_advanced/?tipo=tuberia&acueducto_id=1&stock_bajo=true"

# Validar:
# - Solo tuberías
# - Solo acueducto 1
# - Solo stock bajo
# - Resultados precisos
```

---

## ✅ Checklist de Pruebas

### Endpoint `stock_search`
- [ ] Test 1: Búsqueda exitosa tubería
- [ ] Test 2: Búsqueda exitosa equipo
- [ ] Test 3: Filtro de sucursal
- [ ] Test 4: Error parámetros faltantes
- [ ] Test 5: Error tipo inválido
- [ ] Test 6: Error ID no numérico
- [ ] Test 7: Error artículo no encontrado
- [ ] Test 8: Error sucursal no encontrada
- [ ] Test 9: Sin stock disponible

### Endpoint `stock_search_advanced`
- [ ] Test 10: Búsqueda por nombre
- [ ] Test 11: Búsqueda por sucursal
- [ ] Test 12: Búsqueda por acueducto
- [ ] Test 13: Búsqueda stock bajo
- [ ] Test 14: Búsqueda combinada
- [ ] Test 15: Búsqueda por tipo
- [ ] Test 16: Error sin filtros
- [ ] Test 17: Error ID no numérico
- [ ] Test 18: Sin resultados

### Validación de Datos
- [ ] Test 19: Estructura de respuesta
- [ ] Test 20: Cálculos correctos

### Rendimiento
- [ ] Test 21: Búsqueda rápida
- [ ] Test 22: Búsqueda avanzada rápida

### Casos Reales
- [ ] Caso 1: Verificar stock
- [ ] Caso 2: Stock bajo
- [ ] Caso 3: Búsqueda por sucursal
- [ ] Caso 4: Búsqueda compleja

---

## 📝 Notas

- Todos los tests asumen datos de prueba cargados
- Ajustar IDs según datos disponibles
- Usar `jq` para formatear JSON (opcional)
- Documentar resultados de pruebas

---

**Status**: ✅ LISTO PARA EJECUTAR
