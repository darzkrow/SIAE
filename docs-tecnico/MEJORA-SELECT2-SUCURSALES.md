# ✅ Mejora: Select2 con Sucursales y Acueductos

## 🎯 Problema Identificado

El modal de transferencia solo mostraba un select con todos los acueductos sin agrupar por sucursal, lo que dificultaba la selección.

## ✨ Solución Implementada

Se ha mejorado el modal de transferencia en `Stock.jsx` para agregar un sistema de dos niveles:
1. **Primer Select**: Seleccionar Sucursal
2. **Segundo Select**: Seleccionar Acueducto (filtrado por sucursal)

---

## 🆕 Nuevas Funcionalidades

### 1. Select de Sucursal
- Muestra todas las sucursales disponibles
- Al seleccionar una sucursal, se cargan los acueductos asociados
- Está habilitado siempre

### 2. Select de Acueducto
- Muestra solo los acueductos de la sucursal seleccionada
- Se deshabilita hasta que se seleccione una sucursal
- Muestra mensaje "Primero selecciona una sucursal" cuando está deshabilitado

### 3. Filtrado Automático
- Cuando se selecciona una sucursal, se filtran automáticamente los acueductos
- Si se cambia la sucursal, se limpia la selección anterior de acueducto
- El filtrado es en tiempo real

---

## 📝 Cambios Realizados

### Estados Nuevos
```javascript
const [sucursalDestino, setSucursalDestino] = useState('');
const [sucursales, setSucursales] = useState([]);
const [acueductosFiltered, setAcueductosFiltered] = useState([]);
```

### Fetch de Sucursales
```javascript
// En el useEffect principal
const sucursalesRes = await axios.get(`${API_URL}/api/sucursales/`);
setSucursales(sucursalesRes.data.results || sucursalesRes.data);
```

### useEffect para Filtrado
```javascript
useEffect(() => {
    if (sucursalDestino) {
        const filtered = acueductos.filter(acueducto => 
            acueducto.sucursal === parseInt(sucursalDestino)
        );
        setAcueductosFiltered(filtered);
        setAcueductoDestino('');
    } else {
        setAcueductosFiltered([]);
        setAcueductoDestino('');
    }
}, [sucursalDestino, acueductos]);
```

### Modal Actualizado
```javascript
{movementType === 'TRANSFERENCIA' && (
    <>
        <div>
            <label>Sucursal Destino</label>
            <select value={sucursalDestino} onChange={(e) => setSucursalDestino(e.target.value)}>
                <option value="">Selecciona una sucursal</option>
                {sucursales.map(sucursal => (
                    <option key={sucursal.id} value={sucursal.id}>
                        {sucursal.nombre}
                    </option>
                ))}
            </select>
        </div>

        <div>
            <label>Acueducto Destino</label>
            <select 
                value={acueductoDestino} 
                onChange={(e) => setAcueductoDestino(e.target.value)}
                disabled={!sucursalDestino}
            >
                <option value="">
                    {sucursalDestino ? 'Selecciona un acueducto' : 'Primero selecciona una sucursal'}
                </option>
                {acueductosFiltered.map(acueducto => (
                    <option key={acueducto.id} value={acueducto.id}>
                        {acueducto.nombre}
                    </option>
                ))}
            </select>
        </div>
    </>
)}
```

---

## 🎨 Interfaz

### Modal de Transferencia - Antes
```
┌──────────────────────────────────────┐
│ ↔️ Transferencia                      │
├──────────────────────────────────────┤
│ Artículo: PVC 100mm                  │
│ Acueducto Origen: Sistema Principal  │
│ Acueducto Destino: [dropdown]        │
│   - Sistema Principal                │
│   - Sistema Secundario               │
│   - Sistema Bombeo Orinoco           │
│   - Sistema Tratamiento              │
│   - Sistema Auxiliar                 │
│ Cantidad: [____]                     │
├──────────────────────────────────────┤
│ [Cancelar]  [Guardar]                │
└──────────────────────────────────────┘
```

### Modal de Transferencia - Después
```
┌──────────────────────────────────────┐
│ ↔️ Transferencia                      │
├──────────────────────────────────────┤
│ Artículo: PVC 100mm                  │
│ Acueducto Origen: Sistema Principal  │
│ Sucursal Destino: [dropdown]         │
│   - Planta Caroní                    │
│   - Planta Orinoco                   │
│   - Planta Apure                     │
│ Acueducto Destino: [dropdown]        │
│   (deshabilitado hasta seleccionar)  │
│ Cantidad: [____]                     │
├──────────────────────────────────────┤
│ [Cancelar]  [Guardar]                │
└──────────────────────────────────────┘
```

### Después de Seleccionar Sucursal
```
┌──────────────────────────────────────┐
│ ↔️ Transferencia                      │
├──────────────────────────────────────┤
│ Artículo: PVC 100mm                  │
│ Acueducto Origen: Sistema Principal  │
│ Sucursal Destino: [Planta Caroní ▼]  │
│ Acueducto Destino: [dropdown]        │
│   - Sistema de Bombeo Principal      │
│   - Sistema de Distribución Secundario
│   - Sistema de Emergencia            │
│ Cantidad: [____]                     │
├──────────────────────────────────────┤
│ [Cancelar]  [Guardar]                │
└──────────────────────────────────────┘
```

---

## 🚀 Cómo Usar

### Crear Transferencia
1. Busca el artículo en la tabla de Stock
2. Haz clic en el botón **↔️ Transferencia** (azul)
3. Se abre el modal de transferencia
4. **Selecciona la Sucursal Destino** en el primer dropdown
5. **Selecciona el Acueducto Destino** en el segundo dropdown (ahora habilitado)
6. Ingresa la cantidad
7. Haz clic en "Guardar"

### Validaciones
- ✅ Sucursal destino es requerida
- ✅ Acueducto destino es requerido
- ✅ El segundo select se deshabilita hasta seleccionar sucursal
- ✅ Se muestra mensaje claro cuando está deshabilitado

---

## 📊 Mejoras Implementadas

| Aspecto | Antes | Después |
|--------|-------|---------|
| Selección | Todos los acueductos | Agrupados por sucursal |
| Claridad | Confuso | Claro y organizado |
| UX | Básica | Mejorada |
| Pasos | 1 select | 2 selects (cascada) |
| Validación | Básica | Completa |

---

## 🎯 Beneficios

✅ **Más organizado**: Acueductos agrupados por sucursal
✅ **Más intuitivo**: Flujo lógico (sucursal → acueducto)
✅ **Mejor UX**: Select deshabilitado hasta seleccionar sucursal
✅ **Menos errores**: Validaciones claras
✅ **Más rápido**: Menos opciones para buscar

---

## 🔄 Flujo de Datos

1. Usuario hace clic en botón de transferencia
2. Se abre modal con sucursales cargadas
3. Usuario selecciona sucursal
4. Se filtran acueductos por sucursal
5. Usuario selecciona acueducto
6. Usuario ingresa cantidad
7. Usuario hace clic en "Guardar"
8. Se envía POST a `/api/movimientos/`
9. Backend procesa la transferencia
10. Stock se actualiza automáticamente

---

## 🧪 Casos de Prueba

### Caso 1: Transferencia Entre Sucursales
```
1. Busca "PVC 100mm"
2. Haz clic en ↔️
3. Selecciona "Planta Orinoco"
4. Selecciona "Sistema de Bombeo Orinoco"
5. Ingresa cantidad: 10
6. Haz clic en Guardar
7. Verifica que se movió correctamente
```

### Caso 2: Transferencia Dentro de Sucursal
```
1. Busca "Motor 50 HP"
2. Haz clic en ↔️
3. Selecciona "Planta Caroní"
4. Selecciona "Sistema de Distribución Secundario"
5. Ingresa cantidad: 1
6. Haz clic en Guardar
7. Verifica que se movió correctamente
```

### Caso 3: Validación de Sucursal Requerida
```
1. Busca cualquier artículo
2. Haz clic en ↔️
3. Intenta seleccionar acueducto sin sucursal
4. Verifica que está deshabilitado
5. Selecciona sucursal
6. Verifica que se habilita
```

---

## 📝 Notas

- El filtrado es en tiempo real
- Si se cambia la sucursal, se limpia la selección anterior
- El segundo select muestra un mensaje descriptivo cuando está deshabilitado
- La validación ocurre antes de enviar el movimiento
- Se mantiene la compatibilidad con el resto del sistema

---

## 🔄 Próximas Mejoras

- [ ] Agregar búsqueda en los selects
- [ ] Mostrar cantidad de acueductos por sucursal
- [ ] Agregar iconos para sucursales
- [ ] Mostrar ubicación geográfica
- [ ] Agregar favoritos

---

**Estado**: ✅ Implementado y Funcional
**Fecha**: 2024
**Versión**: 1.2
