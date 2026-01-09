# 🚀 Guía de Uso - MVP Sistema de Inventario Hidroeléctrica

## ✅ Estado: Datos Cargados y Listo para Usar

Se han cargado exitosamente **50+ registros** de datos realistas en la base de datos.

---

## 🎯 Inicio Rápido

### 1. Iniciar Backend
```bash
python manage.py runserver
```
**Resultado**: Backend disponible en `http://localhost:8000`

### 2. Iniciar Frontend
```bash
cd frontend
npm start
```
**Resultado**: Frontend disponible en `http://localhost:3000`

### 3. Acceder a la Aplicación
```
URL: http://localhost:3000
```

### 4. Login
```
Usuario: admin_test
Contraseña: testpass123
```

---

## 📊 Datos Disponibles

### Plantas Hidroeléctricas (5 total)
```
✅ Planta Caroní - Sector A (Principal)
✅ Planta Orinoco - Sector B (Secundaria)
✅ Planta Apure - Sector C (Auxiliar)
✅ Hidrocapital (datos previos)
✅ Hidrocentro (datos previos)
```

### Sistemas de Bombeo/Distribución (10 total)
```
Planta Caroní:
  • Sistema de Bombeo Principal
  • Sistema de Distribución Secundario
  • Sistema de Emergencia

Planta Orinoco:
  • Sistema de Bombeo Orinoco
  • Sistema de Tratamiento

Planta Apure:
  • Sistema Auxiliar de Bombeo

+ 4 sistemas de plantas previas
```

### Tuberías (7 tipos)
```
✅ PVC 100mm - Agua Potable
✅ PVC 75mm - Agua Potable
✅ Hierro Dúctil 150mm - Aguas Servidas
✅ Hierro Dúctil 200mm - Aguas Servidas
✅ Cemento 200mm - Riego
✅ Cemento 250mm - Riego
+ 1 tubería de datos previos
```

### Equipos (12 tipos)
```
✅ Motor Siemens 50 HP
✅ Motor ABB 75 HP
✅ Motor WEG 100 HP
✅ Bomba Grundfos 100m³/h
✅ Bomba Grundfos 150m³/h
✅ Válvula Compuerta 150mm
✅ Válvula Compuerta 200mm
✅ Compresor Atlas Copco 10 HP
✅ Generador Caterpillar 50 kW
✅ Transformador Siemens 100 kVA
✅ Filtro Pentair 50 micras
+ 1 equipo de datos previos
```

### Usuarios (5 total)
```
ADMIN:
  • admin_test / testpass123 (nuevo)
  • admin / admin (previo)

OPERADOR:
  • operador_test / testpass123 (nuevo)
  • supervisor_test / testpass123 (nuevo)
  • admin2 / admin2 (previo)
```

---

## 🎨 Módulos Disponibles

### 1. Dashboard
**Acceso**: Inicio
**Funcionalidades**:
- ✅ Estadísticas generales
- ✅ Stock total
- ✅ Movimientos recientes
- ✅ Alertas críticas
- ✅ Gráficos de tendencias

**Prueba**: Visualiza el resumen de inventario

### 2. Stock
**Acceso**: Menú lateral → Stock
**Funcionalidades**:
- ✅ Ver stock de tuberías por sistema
- ✅ Ver stock de equipos por sistema
- ✅ Filtrar por acueducto/sucursal
- ✅ Búsqueda
- ✅ Alertas visuales

**Prueba**: 
1. Selecciona "Planta Caroní"
2. Visualiza stock de tuberías y equipos
3. Busca "Motor 50 HP"

### 3. Movimientos
**Acceso**: Menú lateral → Movimientos
**Funcionalidades**:
- ✅ Crear entrada de artículos
- ✅ Crear salida de artículos
- ✅ Crear transferencia entre sistemas
- ✅ Filtrar por tipo
- ✅ Ver historial

**Prueba - Entrada**:
1. Haz clic en "Nuevo Movimiento"
2. Tipo: ENTRADA
3. Artículo: Tubería PVC 100mm
4. Acueducto Destino: Sistema de Bombeo Principal
5. Cantidad: 20
6. Haz clic en "Guardar"

**Prueba - Transferencia**:
1. Tipo: TRANSFERENCIA
2. Artículo: Motor 50 HP
3. Acueducto Origen: Sistema de Bombeo Principal
4. Acueducto Destino: Sistema de Distribución Secundario
5. Cantidad: 1
6. Haz clic en "Guardar"

**Prueba - Salida**:
1. Tipo: SALIDA
2. Artículo: Válvula 150mm
3. Acueducto Origen: Sistema de Bombeo Principal
4. Cantidad: 2
5. Haz clic en "Guardar"

### 4. Artículos
**Acceso**: Menú lateral → Artículos
**Funcionalidades**:
- ✅ Ver tuberías
- ✅ Ver equipos
- ✅ Filtrar por categoría
- ✅ Búsqueda
- ✅ Ver detalles

**Prueba**:
1. Selecciona "Tuberías"
2. Visualiza lista de tuberías
3. Busca "PVC"
4. Haz clic en una tubería para ver detalles

### 5. Reportes
**Acceso**: Menú lateral → Reportes
**Funcionalidades**:
- ✅ Dashboard de estadísticas
- ✅ Stock por sucursal
- ✅ Movimientos por período
- ✅ Alertas de stock bajo
- ✅ Exportación de datos

**Prueba**:
1. Visualiza "Stock por Sucursal"
2. Selecciona "Planta Caroní"
3. Ve el stock total de tuberías y equipos
4. Visualiza "Alertas de Stock Bajo"

### 6. Alertas
**Acceso**: Menú lateral → Alertas
**Funcionalidades**:
- ✅ Listar alertas activas
- ✅ Crear nuevas alertas
- ✅ Editar alertas
- ✅ Eliminar alertas
- ✅ Notificaciones

**Prueba**:
1. Visualiza alertas existentes
2. Haz clic en "Nueva Alerta"
3. Artículo: Bomba 100m³/h
4. Acueducto: Sistema de Bombeo Principal
5. Umbral Mínimo: 2
6. Haz clic en "Guardar"

### 7. Usuarios
**Acceso**: Menú lateral → Usuarios (solo Admin)
**Funcionalidades**:
- ✅ Listar usuarios
- ✅ Crear usuarios
- ✅ Editar usuarios
- ✅ Cambiar roles
- ✅ Activar/desactivar

**Prueba**:
1. Haz clic en "Nuevo Usuario"
2. Usuario: prueba_user
3. Email: prueba@test.com
4. Rol: OPERADOR
5. Haz clic en "Guardar"

### 8. Administración
**Acceso**: Menú lateral → Administración (solo Admin)
**Funcionalidades**:
- ✅ CRUD de sucursales
- ✅ CRUD de acueductos
- ✅ CRUD de tuberías
- ✅ CRUD de equipos
- ✅ CRUD de usuarios
- ✅ CRUD de stock

**Prueba**:
1. Selecciona "Sucursales"
2. Visualiza lista de plantas
3. Selecciona "Acueductos"
4. Visualiza sistemas de bombeo
5. Selecciona "Stock Tuberías"
6. Visualiza stock de tuberías

---

## 🧪 Casos de Prueba Recomendados

### Caso 1: Entrada de Artículos
```
Objetivo: Aumentar stock
Pasos:
1. Ir a Movimientos
2. Crear ENTRADA
3. Artículo: Tubería PVC 100mm
4. Cantidad: 50
5. Verificar que stock aumentó
```

### Caso 2: Salida de Artículos
```
Objetivo: Disminuir stock
Pasos:
1. Ir a Movimientos
2. Crear SALIDA
3. Artículo: Motor 50 HP
4. Cantidad: 1
5. Verificar que stock disminuyó
```

### Caso 3: Transferencia Entre Sistemas
```
Objetivo: Mover artículos entre sistemas
Pasos:
1. Ir a Movimientos
2. Crear TRANSFERENCIA
3. Artículo: Válvula 150mm
4. Origen: Sistema Principal
5. Destino: Sistema Secundario
6. Cantidad: 2
7. Verificar que se movió correctamente
```

### Caso 4: Validación de Stock Insuficiente
```
Objetivo: Intentar salida con stock insuficiente
Pasos:
1. Ir a Movimientos
2. Crear SALIDA
3. Artículo: Generador 50 kW
4. Cantidad: 100 (más de lo disponible)
5. Verificar que muestra error
```

### Caso 5: Crear Alerta
```
Objetivo: Crear alerta de stock bajo
Pasos:
1. Ir a Alertas
2. Crear nueva alerta
3. Artículo: Compresor 10 HP
4. Umbral: 1
5. Verificar que se creó
```

### Caso 6: Crear Usuario
```
Objetivo: Crear nuevo usuario (solo Admin)
Pasos:
1. Ir a Usuarios
2. Crear nuevo usuario
3. Usuario: nuevo_operador
4. Email: nuevo@test.com
5. Rol: OPERADOR
6. Verificar que se creó
```

---

## 🔐 Permisos por Rol

### Admin (admin_test)
```
✅ Ver dashboard
✅ Ver stock
✅ Crear movimientos
✅ Ver artículos
✅ Ver reportes
✅ Ver alertas
✅ Crear alertas
✅ Listar usuarios
✅ Crear usuarios
✅ Acceder a administración
✅ CRUD de sucursales
✅ CRUD de acueductos
✅ CRUD de tuberías
✅ CRUD de equipos
✅ CRUD de stock
```

### Operador (operador_test)
```
✅ Ver dashboard
✅ Ver stock
✅ Crear movimientos
✅ Ver artículos
✅ Ver reportes
✅ Ver alertas
❌ Crear alertas
❌ Listar usuarios
❌ Crear usuarios
❌ Acceder a administración
```

---

## 📱 Funcionalidades Principales

### Dashboard
- Estadísticas en tiempo real
- Gráficos de stock
- Movimientos recientes
- Alertas críticas

### Stock
- Visualización por sistema
- Filtros avanzados
- Búsqueda
- Alertas visuales

### Movimientos
- Entrada de artículos
- Salida de artículos
- Transferencia entre sistemas
- Historial completo
- Auditoría

### Reportes
- Stock por sucursal
- Movimientos por período
- Alertas de stock bajo
- Estadísticas generales

### Administración
- Gestión de plantas
- Gestión de sistemas
- Gestión de artículos
- Gestión de usuarios
- Gestión de stock

---

## 🔍 Validaciones Implementadas

### Stock
- ✅ No permite cantidad negativa
- ✅ Valida stock insuficiente en salidas
- ✅ Valida stock insuficiente en transferencias
- ✅ Registra auditoría de operaciones

### Usuarios
- ✅ Valida email único
- ✅ Valida username único
- ✅ Valida rol válido
- ✅ Valida contraseña

### Artículos
- ✅ Valida nombre único
- ✅ Valida número de serie único (equipos)
- ✅ Valida categoría válida
- ✅ Valida propiedades requeridas

---

## 🐛 Solucionar Problemas

### Error: "No se puede conectar al backend"
```
Solución:
1. Verifica que el backend está corriendo: python manage.py runserver
2. Verifica que está en http://localhost:8000
3. Reinicia el backend
```

### Error: "Usuario o contraseña incorrectos"
```
Solución:
1. Verifica que escribiste correctamente: admin_test / testpass123
2. Verifica que los datos se cargaron: python manage.py seed_test_data
3. Limpia el navegador (cookies)
```

### Error: "Stock insuficiente"
```
Solución:
1. Verifica la cantidad disponible en Stock
2. Intenta con una cantidad menor
3. Crea una entrada primero
```

### Error: "Permiso denegado"
```
Solución:
1. Verifica que tienes el rol correcto
2. Admin puede hacer todo
3. Operador solo puede crear movimientos
```

---

## 📊 Estadísticas Actuales

| Concepto | Cantidad |
|----------|----------|
| Plantas | 5 |
| Sistemas | 10 |
| Tuberías | 7 tipos |
| Equipos | 12 tipos |
| Stock Total Tuberías | 215+ unidades |
| Stock Total Equipos | 43+ unidades |
| Alertas Activas | 4 |
| Usuarios | 5 |

---

## 🎓 Próximos Pasos

1. **Explorar Dashboard**: Visualiza las estadísticas
2. **Ver Stock**: Revisa el inventario disponible
3. **Crear Movimientos**: Prueba entrada, salida y transferencia
4. **Ver Reportes**: Analiza los datos
5. **Crear Alertas**: Configura alertas de stock bajo
6. **Administrar Usuarios**: Crea nuevos usuarios (solo Admin)

---

## ✨ Conclusión

El MVP está completamente funcional con datos realistas. Puedes:
- ✅ Visualizar inventario
- ✅ Crear movimientos
- ✅ Generar reportes
- ✅ Gestionar usuarios
- ✅ Configurar alertas
- ✅ Auditar operaciones

**Estado**: 🟢 LISTO PARA USAR

---

**Fecha**: 2024
**Versión**: 1.0
