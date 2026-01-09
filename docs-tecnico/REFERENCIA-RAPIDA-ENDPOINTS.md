# Referencia Rápida - Endpoints de Búsqueda

**Última Actualización**: 8 de Enero de 2026

---

## 🔍 Búsqueda de Stock por Artículo

### Endpoint
```
GET /api/reportes/stock_search/
```

### Parámetros
```
articulo_id=1&tipo=tuberia&sucursal_id=1
```

### Ejemplo
```bash
curl "http://localhost:8000/api/reportes/stock_search/?articulo_id=1&tipo=tuberia"
```

### Respuesta
```json
{
  "articulo_id": 1,
  "articulo": "Tubería PVC 2 pulgadas",
  "tipo": "tuberia",
  "total_ubicaciones": 3,
  "stock_total": 150,
  "resultados": [
    {
      "id": 10,
      "articulo": "Tubería PVC 2 pulgadas",
      "cantidad": 50,
      "acueducto": "Sistema Principal",
      "sucursal": "Planta A",
      "estado": "normal"
    }
  ]
}
```

---

## 🔎 Búsqueda Avanzada

### Endpoint
```
GET /api/reportes/stock_search_advanced/
```

### Parámetros
```
nombre=tuberia&sucursal_id=1&stock_bajo=true&tipo=all
```

### Ejemplos

**Por Nombre**:
```bash
curl "http://localhost:8000/api/reportes/stock_search_advanced/?nombre=motor"
```

**Por Sucursal**:
```bash
curl "http://localhost:8000/api/reportes/stock_search_advanced/?sucursal_id=1"
```

**Stock Bajo**:
```bash
curl "http://localhost:8000/api/reportes/stock_search_advanced/?stock_bajo=true"
```

**Combinado**:
```bash
curl "http://localhost:8000/api/reportes/stock_search_advanced/?nombre=motor&tipo=equipo&stock_bajo=true"
```

### Respuesta
```json
{
  "filtros": {
    "nombre": "motor",
    "sucursal_id": null,
    "tipo": "equipo",
    "stock_bajo": true
  },
  "total_resultados": 2,
  "stock_total": 8,
  "resultados": [
    {
      "id": 25,
      "articulo": "Motor de Bombeo 5HP",
      "cantidad": 3,
      "acueducto": "Sistema Principal",
      "sucursal": "Planta A",
      "estado": "bajo"
    }
  ]
}
```

---

## ✅ Validaciones

### Errores Comunes

| Error | Solución |
|-------|----------|
| 400 - Parámetros faltantes | Proporcionar `articulo_id` y `tipo` |
| 400 - Tipo inválido | Usar `tuberia` o `equipo` |
| 400 - ID no numérico | Usar número entero |
| 404 - Artículo no encontrado | Verificar ID del artículo |
| 404 - Sucursal no encontrada | Verificar ID de sucursal |

---

## 📊 Estados de Stock

| Estado | Condición | Color |
|--------|-----------|-------|
| normal | cantidad > 10 | Verde |
| bajo | cantidad ≤ 10 | Amarillo |
| sin stock | cantidad = 0 | Rojo |

---

## 🎯 Casos de Uso Rápidos

### Verificar Stock de Artículo
```bash
curl "http://localhost:8000/api/reportes/stock_search/?articulo_id=1&tipo=tuberia"
```

### Buscar Artículos con Stock Bajo
```bash
curl "http://localhost:8000/api/reportes/stock_search_advanced/?stock_bajo=true"
```

### Buscar en Sucursal Específica
```bash
curl "http://localhost:8000/api/reportes/stock_search_advanced/?sucursal_id=1"
```

### Buscar por Nombre
```bash
curl "http://localhost:8000/api/reportes/stock_search_advanced/?nombre=motor"
```

---

## 📝 Campos de Respuesta

```json
{
  "id": 10,                              // ID del stock
  "articulo": "Tubería PVC 2 pulgadas",  // Nombre del artículo
  "articulo_id": 1,                      // ID del artículo
  "tipo": "tuberia",                     // Tipo: tuberia/equipo
  "acueducto": "Sistema Principal",      // Nombre del acueducto
  "acueducto_id": 1,                     // ID del acueducto
  "sucursal": "Planta A",                // Nombre de la sucursal
  "sucursal_id": 1,                      // ID de la sucursal
  "cantidad": 50,                        // Cantidad disponible
  "fecha_actualizacion": "2026-01-08",   // Última actualización
  "estado": "normal"                     // Estado: normal/bajo
}
```

---

## 🔗 Todos los Endpoints

```
GET /api/reportes/dashboard_stats/
GET /api/reportes/stock_por_sucursal/
GET /api/reportes/movimientos_recientes/
GET /api/reportes/alertas_stock_bajo/
GET /api/reportes/resumen_movimientos/
GET /api/reportes/stock_search/
GET /api/reportes/stock_search_advanced/
```

---

## 📚 Documentación Completa

- `docs-tecnico/ENDPOINTS-BUSQUEDA-STOCK.md` - Documentación técnica
- `docs-tecnico/VALIDACIONES-SISTEMA.md` - Validaciones
- `docs-tecnico/PRUEBAS-ENDPOINTS-BUSQUEDA.md` - Guía de pruebas

---

**Última Actualización**: 8 de Enero de 2026
