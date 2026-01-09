# Validaciones del Sistema - Documentación Completa

**Fecha**: 8 de Enero de 2026  
**Status**: ✅ IMPLEMENTADO

---

## 📋 Resumen

Documentación completa de todas las validaciones implementadas en el sistema a nivel de frontend, backend y API.

---

## 🔐 Validaciones de Entrada

### 1. Validaciones de Parámetros API

#### Endpoint: `stock_search`

| Validación | Tipo | Acción |
|-----------|------|--------|
| `articulo_id` requerido | Obligatorio | Error 400 |
| `tipo` requerido | Obligatorio | Error 400 |
| `articulo_id` numérico | Tipo | Error 400 |
| `tipo` válido (tuberia/equipo) | Enum | Error 400 |
| `sucursal_id` numérico | Tipo | Error 400 |
| Sucursal existe | Existencia | Error 404 |
| Artículo existe | Existencia | Error 404 |
| Stock disponible | Lógica | Mensaje informativo |

#### Endpoint: `stock_search_advanced`

| Validación | Tipo | Acción |
|-----------|------|--------|
| Al menos un filtro | Obligatorio | Error 400 |
| `sucursal_id` numérico | Tipo | Error 400 |
| `acueducto_id` numérico | Tipo | Error 400 |
| `stock_bajo` booleano | Tipo | Conversión automática |
| `tipo` válido | Enum | Default: 'all' |

---

## 📝 Validaciones de Movimientos

### Frontend: Stock.jsx

#### Validación 1: Cantidad Válida
```javascript
if (!movementQuantity || movementQuantity <= 0) {
    // Error: Cantidad Inválida
}
```
- **Condición**: Cantidad debe ser > 0
- **Mensaje**: "Ingresa una cantidad válida mayor a 0"
- **Tipo**: Warning (SweetAlert)

#### Validación 2: Acueducto Destino Requerido
```javascript
if (movementType === 'TRANSFERENCIA' && !acueductoDestino) {
    // Error: Acueducto Requerido
}
```
- **Condición**: En transferencias, destino es obligatorio
- **Mensaje**: "Selecciona un acueducto destino"
- **Tipo**: Warning (SweetAlert)

#### Validación 3: Origen ≠ Destino
```javascript
if (movementType === 'TRANSFERENCIA' && 
    parseInt(acueductoDestino) === selectedItem.acueducto) {
    // Error: Acueducto Inválido
}
```
- **Condición**: Origen y destino deben ser diferentes
- **Mensaje**: "El acueducto destino no puede ser igual al acueducto origen"
- **Tipo**: Warning (SweetAlert)

### Frontend: Movimientos.jsx

#### Validación 1: Origen ≠ Destino
```javascript
if (formData.tipo_movimiento === 'TRANSFERENCIA' && 
    formData.acueducto_origen === formData.acueducto_destino) {
    // Error: Acueducto Inválido
}
```
- **Condición**: En transferencias, origen ≠ destino
- **Mensaje**: "El acueducto destino no puede ser igual al acueducto origen"
- **Tipo**: Warning (SweetAlert)

---

## 🔄 Validaciones de Lógica de Negocio

### Movimientos de Inventario

#### Tipo: ENTRADA
- ✅ Requiere: `acueducto_destino`
- ✅ Requiere: `cantidad` > 0
- ✅ Requiere: `articulo` (tuberia o equipo)
- ✅ Efecto: Aumenta stock en destino

#### Tipo: SALIDA
- ✅ Requiere: `acueducto_origen`
- ✅ Requiere: `cantidad` > 0
- ✅ Requiere: `articulo`
- ✅ Requiere: Stock disponible ≥ cantidad
- ✅ Efecto: Disminuye stock en origen

#### Tipo: TRANSFERENCIA
- ✅ Requiere: `acueducto_origen` ≠ `acueducto_destino`
- ✅ Requiere: `cantidad` > 0
- ✅ Requiere: `articulo`
- ✅ Requiere: Stock disponible ≥ cantidad
- ✅ Efecto: Disminuye origen, aumenta destino (si sucursales diferentes)
- ✅ Efecto: Solo cambia ubicación (si misma sucursal)

#### Tipo: AJUSTE
- ✅ Requiere: `acueducto_origen`
- ✅ Requiere: `cantidad` (puede ser positiva o negativa)
- ✅ Requiere: `articulo`
- ✅ Efecto: Ajusta stock en ubicación

---

## 🎯 Validaciones de Cascada de Selects

### Stock.jsx - Cascada Sucursal → Acueducto

#### Paso 1: Seleccionar Sucursal
```javascript
if (sucursalDestino) {
    const filtered = acueductos.filter(acueducto => 
        acueducto.sucursal === parseInt(sucursalDestino)
    );
    setAcueductosFiltered(filtered);
    setAcueductoDestino(''); // Limpiar selección anterior
}
```
- **Acción**: Filtra acueductos por sucursal
- **Efecto**: Limpia selección anterior de acueducto

#### Paso 2: Seleccionar Acueducto
```javascript
// Select deshabilitado hasta seleccionar sucursal
disabled={!sucursalDestino}
```
- **Condición**: Acueducto solo habilitado si sucursal seleccionada
- **Mensaje**: "Primero selecciona una sucursal"

---

## 📊 Validaciones de Stock

### Umbral de Stock Bajo
```javascript
const getStockStatus = (cantidad, umbral) => {
    if (cantidad === 0) return { color: 'bg-red-100 text-red-800', label: 'Sin stock' };
    if (cantidad <= umbral) return { color: 'bg-yellow-100 text-yellow-800', label: 'Bajo' };
    return { color: 'bg-green-100 text-green-800', label: 'Normal' };
};
```

| Estado | Condición | Color | Acción |
|--------|-----------|-------|--------|
| Sin stock | cantidad = 0 | Rojo | Alerta crítica |
| Bajo | cantidad ≤ 10 | Amarillo | Alerta |
| Normal | cantidad > 10 | Verde | OK |

---

## 🔍 Validaciones de Búsqueda

### stock_search

1. **Validación de Parámetros**
   - `articulo_id`: Requerido, numérico
   - `tipo`: Requerido, enum (tuberia/equipo)
   - `sucursal_id`: Opcional, numérico

2. **Validación de Existencia**
   - Artículo debe existir
   - Sucursal debe existir (si se proporciona)

3. **Validación de Disponibilidad**
   - Stock debe estar disponible
   - Retorna mensaje si no hay stock

### stock_search_advanced

1. **Validación de Filtros**
   - Al menos uno requerido: nombre, sucursal_id, acueducto_id
   - Todos opcionales pero al menos uno obligatorio

2. **Validación de Tipos**
   - `sucursal_id`: Numérico
   - `acueducto_id`: Numérico
   - `stock_bajo`: Booleano
   - `tipo`: Enum (tuberia/equipo/all)

3. **Validación de Búsqueda**
   - Búsqueda case-insensitive
   - Busca en nombre y descripción
   - Soporta búsqueda parcial

---

## 🛡️ Validaciones de Seguridad

### Autenticación
- ✅ Token JWT requerido
- ✅ Usuario debe estar autenticado
- ✅ Sesión válida

### Autorización
- ✅ ADMIN: Acceso completo
- ✅ OPERADOR: Solo su sucursal
- ✅ Filtrado automático por rol

### Validación de Datos
- ✅ Prevención de inyección SQL (ORM)
- ✅ Validación de tipos
- ✅ Sanitización de entrada
- ✅ Manejo de errores seguro

---

## 📋 Matriz de Validaciones

### Por Módulo

#### Dashboard
| Validación | Tipo | Status |
|-----------|------|--------|
| Autenticación | Seguridad | ✅ |
| Rol diferenciado | Autorización | ✅ |
| Datos en tiempo real | Lógica | ✅ |
| Manejo de errores | Robustez | ✅ |

#### Stock
| Validación | Tipo | Status |
|-----------|------|--------|
| Búsqueda y filtros | Funcionalidad | ✅ |
| Cascada de selects | UX | ✅ |
| Validación origen ≠ destino | Lógica | ✅ |
| Cantidad válida | Lógica | ✅ |
| Stock disponible | Lógica | ✅ |

#### Movimientos
| Validación | Tipo | Status |
|-----------|------|--------|
| Tipo de movimiento | Lógica | ✅ |
| Artículo requerido | Lógica | ✅ |
| Cantidad válida | Lógica | ✅ |
| Origen ≠ destino | Lógica | ✅ |
| Stock disponible | Lógica | ✅ |

#### Búsqueda
| Validación | Tipo | Status |
|-----------|------|--------|
| Parámetros requeridos | Entrada | ✅ |
| Tipos numéricos | Entrada | ✅ |
| Existencia de registros | Lógica | ✅ |
| Búsqueda case-insensitive | Funcionalidad | ✅ |

---

## 🎯 Flujo de Validación Completo

### Crear Movimiento desde Stock

```
1. Usuario selecciona artículo
   ↓
2. Selecciona tipo de movimiento (ENTRADA/SALIDA/TRANSFERENCIA)
   ↓
3. Si TRANSFERENCIA:
   a. Selecciona sucursal destino
   b. Selecciona acueducto destino (filtrado)
   c. Valida: origen ≠ destino
   ↓
4. Ingresa cantidad
   a. Valida: cantidad > 0
   b. Valida: cantidad ≤ stock disponible
   ↓
5. Envía a API
   ↓
6. Backend valida:
   a. Artículo existe
   b. Acueductos existen
   c. Stock disponible
   d. Lógica de negocio
   ↓
7. Procesa movimiento
   ↓
8. Retorna resultado
   ↓
9. Frontend muestra SweetAlert
   ↓
10. Recarga datos
```

---

## 📊 Mensajes de Error

### Errores de Entrada (400)

| Error | Mensaje | Solución |
|-------|---------|----------|
| Parámetro faltante | "Se requieren parámetros: ..." | Proporcionar parámetro |
| Tipo inválido | "Tipo de artículo inválido" | Usar tuberia o equipo |
| ID no numérico | "articulo_id debe ser un número válido" | Usar número entero |
| Sin filtros | "Se requiere al menos uno de: ..." | Proporcionar filtro |

### Errores de Existencia (404)

| Error | Mensaje | Solución |
|-------|---------|----------|
| Artículo no encontrado | "Tubería con ID X no encontrada" | Verificar ID |
| Sucursal no encontrada | "Sucursal con ID X no encontrada" | Verificar ID |
| Acueducto no encontrado | "Acueducto con ID X no encontrada" | Verificar ID |

### Errores de Lógica (400)

| Error | Mensaje | Solución |
|-------|---------|----------|
| Cantidad inválida | "Cantidad debe ser mayor a 0" | Ingresar cantidad válida |
| Origen = Destino | "El acueducto destino no puede ser igual al origen" | Seleccionar acueducto diferente |
| Stock insuficiente | "Stock insuficiente" | Reducir cantidad |

---

## 🧪 Pruebas de Validación

### Test 1: Validación de Cantidad
```javascript
// Debe fallar
movementQuantity = 0;
movementQuantity = -5;
movementQuantity = "";

// Debe pasar
movementQuantity = 1;
movementQuantity = 100;
```

### Test 2: Validación de Acueductos
```javascript
// Debe fallar
acueductoDestino = selectedItem.acueducto;

// Debe pasar
acueductoDestino = diferentAcueducto;
```

### Test 3: Validación de Búsqueda
```bash
# Debe fallar (sin parámetros)
curl "http://localhost:8000/api/reportes/stock_search/"

# Debe pasar
curl "http://localhost:8000/api/reportes/stock_search/?articulo_id=1&tipo=tuberia"
```

---

## 📈 Mejoras Futuras

1. **Validaciones Adicionales**
   - Validación de permisos por acueducto
   - Validación de horarios de operación
   - Validación de límites de cantidad

2. **Mensajes Mejorados**
   - Mensajes multiidioma
   - Sugerencias de corrección
   - Códigos de error estandarizados

3. **Auditoría**
   - Registro de intentos fallidos
   - Alertas de validaciones críticas
   - Reportes de errores

---

**Status**: ✅ COMPLETADO Y FUNCIONAL
