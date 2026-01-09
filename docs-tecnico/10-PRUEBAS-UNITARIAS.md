# 🧪 Pruebas Unitarias - Sistema de Inventario Hidroeléctrica

## Descripción General

Se han creado pruebas unitarias completas para validar la funcionalidad del MVP del sistema de inventario. Las pruebas cubren:

- **Modelos**: Validación de lógica de negocio
- **Serializers**: Serialización/deserialización de datos
- **API REST**: Endpoints y permisos
- **Movimientos**: Lógica de transferencias entre sucursales y acueductos
- **Auditoría**: Registro de operaciones

## Estructura de Pruebas

### 1. Pruebas de Modelos (`inventario/tests.py`)

#### SetupTestDataMixin
Proporciona datos de prueba realistas para una hidroeléctrica:
- **Organización**: Hidroeléctrica Central
- **Sucursales**: 3 plantas (Caroní, Orinoco, Apure)
- **Acueductos**: Sistemas de bombeo, distribución, tratamiento
- **Tuberías**: PVC, Hierro Dúctil, Cemento (diferentes diámetros y usos)
- **Equipos**: Motores de bombeo, bombas, válvulas, compresores, generadores
- **Usuarios**: Admin y Operador

#### Clases de Prueba

**TuberiaModelTests**
- Crear tuberías de diferentes materiales
- Validar propiedades (diámetro, longitud, uso)
- Representación en string

**EquipoModelTests**
- Crear equipos operativos (motores, bombas, válvulas)
- Validar unicidad de número de serie
- Propiedades de potencia y marca

**StockTuberiaModelTests**
- Crear stock de tuberías
- Validar cantidad no negativa
- Restricción unique_together

**MovimientoInventarioTests** (CRÍTICO)
- ✅ Entrada de tuberías
- ✅ Salida de tuberías
- ✅ Validación de stock insuficiente
- ✅ **Transferencia entre sucursales** (disminuye origen, aumenta destino)
- ✅ **Transferencia mismo acueducto** (solo cambio de ubicación)
- ✅ Entrada de equipos
- ✅ Auditoría de movimientos exitosos
- ✅ Auditoría de movimientos fallidos

**AlertaStockTests**
- Crear alertas para tuberías
- Crear alertas para equipos
- Validar que no permite ambos artículos

**SerializerTests**
- Serializar/deserializar tuberías
- Serializar/deserializar equipos
- Serializar/deserializar stock

### 2. Pruebas de API (`inventario/test_api.py`)

#### APISetupMixin
Configura datos base para pruebas de API

#### Clases de Prueba

**TuberiaAPITests**
- Listar tuberías (con/sin autenticación)
- Crear tubería (permisos por rol)
- Actualizar tubería
- Eliminar tubería

**EquipoAPITests**
- Listar equipos
- Crear equipo (solo admin)
- Validar número de serie único

**StockAPITests**
- Listar stock de tuberías y equipos
- Crear stock
- Actualizar cantidad

**MovimientoAPITests**
- Crear entrada
- Crear salida
- Crear transferencia
- Validar stock insuficiente
- Filtrar por tipo
- Paginación

**UsuariosAPITests**
- Listar usuarios (solo admin)
- Crear usuario (solo admin)
- Obtener perfil del usuario

**AuditoriaAPITests**
- Listar auditorías
- Filtrar por status

**ReportesAPITests**
- Dashboard stats
- Stock por sucursal
- Alertas de stock bajo

## Datos de Prueba Realistas

### Plantas Hidroeléctricas
```
Planta Caroní - Sector A (Principal)
├── Sistema de Bombeo Principal
├── Sistema de Distribución Secundario
└── Sistema de Emergencia

Planta Orinoco - Sector B (Secundaria)
├── Sistema de Bombeo Orinoco
└── Sistema de Tratamiento

Planta Apure - Sector C (Auxiliar)
└── Sistema Auxiliar de Bombeo
```

### Tuberías (Artículos Operativos)
- **PVC 100mm**: Agua potable (50 unidades)
- **PVC 75mm**: Agua potable (40 unidades)
- **Hierro Dúctil 150mm**: Aguas servidas (25 unidades)
- **Hierro Dúctil 200mm**: Aguas servidas (20 unidades)
- **Cemento 200mm**: Riego (35 unidades)
- **Cemento 250mm**: Riego (15 unidades)

### Equipos (Motores de Bombeo y Operativos)
- **Motor Siemens 50 HP**: 3 unidades
- **Motor ABB 75 HP**: 2 unidades
- **Motor WEG 100 HP**: 1 unidad
- **Bomba Grundfos 100m³/h**: 5 unidades
- **Bomba Grundfos 150m³/h**: 3 unidades
- **Válvula Compuerta 150mm**: 8 unidades
- **Válvula Compuerta 200mm**: 6 unidades
- **Compresor Atlas Copco 10 HP**: 2 unidades
- **Generador Caterpillar 50 kW**: 1 unidad
- **Transformador Siemens 100 kVA**: 2 unidades
- **Filtro Pentair 50 micras**: 10 unidades

### Usuarios de Prueba
- **admin_test** (ADMIN): admin@test.com
- **operador_test** (OPERADOR): operador@test.com
- **supervisor_test** (OPERADOR): supervisor@test.com

Contraseña: `testpass123`

## Ejecución de Pruebas

### 1. Generar Datos de Prueba

```bash
# Generar datos realistas para una hidroeléctrica
python manage.py seed_test_data
```

Esto crea:
- 3 sucursales (plantas)
- 7 acueductos (sistemas)
- 6 tuberías de diferentes tipos
- 11 equipos operativos
- Stock inicial para cada artículo
- Alertas de stock bajo
- 3 usuarios de prueba

### 2. Ejecutar Todas las Pruebas

```bash
# Ejecutar todas las pruebas
python manage.py test inventario

# Con verbosidad
python manage.py test inventario -v 2

# Con cobertura
coverage run --source='inventario' manage.py test inventario
coverage report
coverage html
```

### 3. Ejecutar Pruebas Específicas

```bash
# Solo pruebas de modelos
python manage.py test inventario.tests

# Solo pruebas de API
python manage.py test inventario.test_api

# Solo pruebas de movimientos
python manage.py test inventario.tests.MovimientoInventarioTests

# Solo pruebas de transferencias
python manage.py test inventario.tests.MovimientoInventarioTests.test_transferencia_entre_sucursales
python manage.py test inventario.tests.MovimientoInventarioTests.test_transferencia_mismo_acueducto_diferente_sucursal
```

### 4. Ejecutar Pruebas de API Específicas

```bash
# Pruebas de movimientos
python manage.py test inventario.test_api.MovimientoAPITests

# Pruebas de usuarios
python manage.py test inventario.test_api.UsuariosAPITests

# Pruebas de reportes
python manage.py test inventario.test_api.ReportesAPITests
```

## Casos de Prueba Críticos

### Movimiento de Inventario

#### ✅ Transferencia Entre Sucursales
```
Origen: Planta Caroní - Sistema de Bombeo Principal (50 tuberías)
Destino: Planta Orinoco - Sistema de Bombeo Orinoco (0 tuberías)
Cantidad: 15 tuberías

Resultado:
- Planta Caroní: 50 - 15 = 35 ✓
- Planta Orinoco: 0 + 15 = 15 ✓
```

#### ✅ Transferencia Mismo Acueducto (Cambio de Ubicación)
```
Origen: Planta Caroní - Sistema de Bombeo Principal (50 tuberías)
Destino: Planta Caroní - Sistema de Distribución Secundario (0 tuberías)
Cantidad: 10 tuberías

Resultado:
- Sistema Principal: 50 - 10 = 40 ✓
- Sistema Secundario: 0 + 10 = 10 ✓
- Total Planta Caroní: 40 + 10 = 50 (sin cambio) ✓
```

#### ✅ Entrada de Artículos
```
Destino: Planta Caroní - Sistema de Bombeo Principal
Cantidad: 20 tuberías

Resultado:
- Stock: 50 + 20 = 70 ✓
```

#### ✅ Salida de Artículos
```
Origen: Planta Caroní - Sistema de Bombeo Principal (50 tuberías)
Cantidad: 10 tuberías

Resultado:
- Stock: 50 - 10 = 40 ✓
```

#### ❌ Salida con Stock Insuficiente
```
Origen: Planta Caroní - Sistema de Bombeo Principal (50 tuberías)
Cantidad: 1000 tuberías (INSUFICIENTE)

Resultado:
- Error: ValidationError ✓
- Stock sin cambios: 50 ✓
```

## Validación de Permisos

### Admin (ADMIN)
- ✅ Crear tuberías
- ✅ Crear equipos
- ✅ Crear stock
- ✅ Crear movimientos
- ✅ Listar usuarios
- ✅ Crear usuarios
- ✅ Ver auditorías

### Operador (OPERADOR)
- ✅ Listar tuberías
- ✅ Listar equipos
- ✅ Listar stock
- ✅ Crear movimientos
- ❌ Crear tuberías (403 Forbidden)
- ❌ Listar usuarios (403 Forbidden)
- ❌ Ver auditorías (403 Forbidden)

## Auditoría de Operaciones

Cada movimiento genera un registro de auditoría con:
- Status: SUCCESS o FAILED
- Tipo de artículo: TUBERIA o EQUIPO
- Nombre del artículo
- Tipo de movimiento: ENTRADA, SALIDA, TRANSFERENCIA, AJUSTE
- Cantidad
- Acueducto origen/destino
- Mensaje de error (si aplica)
- Fecha y hora

## Cobertura de Pruebas

### Modelos
- ✅ Creación de tuberías
- ✅ Creación de equipos
- ✅ Validación de stock
- ✅ Movimientos de inventario
- ✅ Alertas de stock
- ✅ Auditoría

### API
- ✅ Autenticación
- ✅ Permisos por rol
- ✅ CRUD de artículos
- ✅ CRUD de stock
- ✅ Movimientos
- ✅ Usuarios
- ✅ Reportes

### Lógica de Negocio
- ✅ Transferencias entre sucursales
- ✅ Cambios de ubicación dentro de sucursal
- ✅ Validación de stock
- ✅ Alertas de stock bajo
- ✅ Auditoría de operaciones

## Próximos Pasos

1. **Ejecutar pruebas**: `python manage.py test inventario -v 2`
2. **Generar datos**: `python manage.py seed_test_data`
3. **Verificar cobertura**: `coverage report`
4. **Validar en frontend**: Usar credenciales de prueba para probar la UI

## Notas Importantes

- Las pruebas usan `TransactionTestCase` para movimientos (requiere transacciones)
- Los datos de prueba son realistas para una hidroeléctrica operativa
- Se valida la lógica crítica de transferencias entre sucursales vs. cambios de ubicación
- Todos los permisos se validan según el rol del usuario
- La auditoría registra tanto operaciones exitosas como fallidas
