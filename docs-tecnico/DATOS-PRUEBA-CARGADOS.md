# ✅ Datos de Prueba - Cargados en el MVP

## 📊 Resumen de Datos Generados

Se han cargado exitosamente **50+ registros** de datos realistas en la base de datos del MVP.

---

## 🏢 Plantas Hidroeléctricas (3)

### 1. Planta Caroní - Sector A (Principal)
- **Organización**: Hidroeléctrica Central Caroní
- **RIF**: J-12345678-9
- **Sistemas**: 3

### 2. Planta Orinoco - Sector B (Secundaria)
- **Organización**: Hidroeléctrica Central Caroní
- **Sistemas**: 2

### 3. Planta Apure - Sector C (Auxiliar)
- **Organización**: Hidroeléctrica Central Caroní
- **Sistemas**: 1

---

## 🔧 Sistemas de Bombeo/Distribución (7)

### Planta Caroní
1. **Sistema de Bombeo Principal**
   - Stock de tuberías: 50 + 40 = 90 unidades
   - Stock de equipos: 3 + 2 + 5 + 8 + 2 = 20 unidades

2. **Sistema de Distribución Secundario**
   - Stock de tuberías: 30 unidades
   - Stock de equipos: 6 unidades

3. **Sistema de Emergencia**
   - Stock de equipos: 2 + 1 = 3 unidades

### Planta Orinoco
4. **Sistema de Bombeo Orinoco**
   - Stock de equipos: 1 unidad

5. **Sistema de Tratamiento**
   - Stock de tuberías: 20 unidades
   - Stock de equipos: 3 + 10 = 13 unidades

### Planta Apure
6. **Sistema Auxiliar de Bombeo**
   - Stock de tuberías: 35 + 15 = 50 unidades

---

## 🔩 Tuberías (6 tipos)

### Agua Potable (PVC)
| Artículo | Diámetro | Longitud | Stock Total | Ubicación |
|----------|----------|----------|-------------|-----------|
| Tubería PVC 100mm | 100mm | 50m | 80 | Sistema Principal (50) + Sistema Secundario (30) |
| Tubería PVC 75mm | 75mm | 50m | 40 | Sistema Principal |

### Aguas Servidas (Hierro Dúctil)
| Artículo | Diámetro | Longitud | Stock Total | Ubicación |
|----------|----------|----------|-------------|-----------|
| Tubería Hierro 150mm | 150mm | 100m | 25 | Sistema Principal |
| Tubería Hierro 200mm | 200mm | 100m | 20 | Sistema Tratamiento |

### Riego (Cemento)
| Artículo | Diámetro | Longitud | Stock Total | Ubicación |
|----------|----------|----------|-------------|-----------|
| Tubería Cemento 200mm | 200mm | 75m | 35 | Sistema Auxiliar |
| Tubería Cemento 250mm | 250mm | 75m | 15 | Sistema Auxiliar |

**Total Tuberías**: 215 unidades

---

## ⚙️ Equipos Operativos (11)

### Motores de Bombeo
| Equipo | Marca | Modelo | Potencia | Serie | Stock |
|--------|-------|--------|----------|-------|-------|
| Motor 50 HP | Siemens | IE3-100L-4 | 50 HP | SIE-2024-001 | 3 |
| Motor 75 HP | ABB | M3BP-225M-4 | 75 HP | ABB-2024-001 | 2 |
| Motor 100 HP | WEG | W22-100L-4 | 100 HP | WEG-2024-001 | 1 |

### Bombas Centrífugas
| Equipo | Marca | Modelo | Potencia | Serie | Stock |
|--------|-------|--------|----------|-------|-------|
| Bomba 100m³/h | Grundfos | CR-100-2-2 | 30 HP | GRU-2024-001 | 5 |
| Bomba 150m³/h | Grundfos | CR-150-2-2 | 45 HP | GRU-2024-002 | 3 |

### Válvulas
| Equipo | Marca | Modelo | Serie | Stock |
|--------|-------|--------|-------|-------|
| Válvula 150mm | Watts | WC-150 | WAT-2024-001 | 8 |
| Válvula 200mm | Watts | WC-200 | WAT-2024-002 | 6 |

### Otros Equipos
| Equipo | Marca | Modelo | Potencia | Serie | Stock |
|--------|-------|--------|----------|-------|-------|
| Compresor 10 HP | Atlas Copco | GA-10 | 10 HP | ATC-2024-001 | 2 |
| Generador 50 kW | Caterpillar | C50 | 50 kW | CAT-2024-001 | 1 |
| Transformador 100 kVA | Siemens | SIEMENS-100 | - | SIE-TRANS-001 | 2 |
| Filtro 50 micras | Pentair | FIL-50 | - | PEN-2024-001 | 10 |

**Total Equipos**: 43 unidades

---

## 👥 Usuarios de Prueba (3)

### Admin
```
Usuario: admin_test
Contraseña: testpass123
Email: admin@test.com
Rol: ADMIN
Permisos: Crear artículos, listar usuarios, ver auditorías
```

### Operador 1
```
Usuario: operador_test
Contraseña: testpass123
Email: operador@test.com
Rol: OPERADOR
Permisos: Listar artículos, crear movimientos
```

### Operador 2
```
Usuario: supervisor_test
Contraseña: testpass123
Email: supervisor@test.com
Rol: OPERADOR
Permisos: Listar artículos, crear movimientos
```

---

## 🚨 Alertas de Stock Bajo (4)

| Artículo | Acueducto | Umbral Mínimo | Estado |
|----------|-----------|---------------|--------|
| Tubería PVC 100mm | Sistema Principal | 20 | Activa |
| Motor 50 HP | Sistema Principal | 1 | Activa |
| Bomba 100m³/h | Sistema Principal | 2 | Activa |
| Válvula 150mm | Sistema Principal | 3 | Activa |

---

## 📊 Estadísticas Totales

| Concepto | Cantidad |
|----------|----------|
| Plantas | 3 |
| Sistemas | 7 |
| Categorías | 8 |
| Tuberías | 6 tipos |
| Equipos | 11 tipos |
| Stock Total Tuberías | 215 unidades |
| Stock Total Equipos | 43 unidades |
| Alertas Activas | 4 |
| Usuarios | 3 |

---

## 🎯 Cómo Usar los Datos

### 1. Acceder al Sistema
```
URL: http://localhost:3000
```

### 2. Login como Admin
```
Usuario: admin_test
Contraseña: testpass123
```

### 3. Explorar Módulos
- **Dashboard**: Ver estadísticas generales
- **Stock**: Ver inventario de tuberías y equipos
- **Movimientos**: Crear movimientos de entrada/salida/transferencia
- **Artículos**: Ver detalles de tuberías y equipos
- **Reportes**: Ver reportes de stock y alertas
- **Administración**: Gestionar plantas, sistemas, usuarios
- **Usuarios**: Crear/editar usuarios

### 4. Crear Movimientos de Prueba
```
Ejemplo 1: Entrada de tuberías
- Artículo: Tubería PVC 100mm
- Acueducto Destino: Sistema Principal
- Cantidad: 20
- Tipo: ENTRADA

Ejemplo 2: Transferencia entre sistemas
- Artículo: Motor 50 HP
- Acueducto Origen: Sistema Principal
- Acueducto Destino: Sistema Secundario
- Cantidad: 1
- Tipo: TRANSFERENCIA

Ejemplo 3: Salida de artículos
- Artículo: Válvula 150mm
- Acueducto Origen: Sistema Principal
- Cantidad: 2
- Tipo: SALIDA
```

---

## 🔍 Validaciones Disponibles

### Stock Insuficiente
```
Intenta hacer una salida de 1000 tuberías
Resultado: Error - Stock insuficiente
```

### Transferencia Entre Sucursales
```
Transferir 10 tuberías de Planta Caroní a Planta Orinoco
Resultado: Planta Caroní disminuye, Planta Orinoco aumenta
```

### Cambio de Ubicación
```
Transferir 5 tuberías dentro de Planta Caroní
Resultado: Total de Planta se mantiene, solo cambia ubicación
```

---

## 📱 Funcionalidades para Probar

### Dashboard
- ✅ Estadísticas generales
- ✅ Stock total
- ✅ Movimientos recientes
- ✅ Alertas críticas

### Stock
- ✅ Listar tuberías por sistema
- ✅ Listar equipos por sistema
- ✅ Filtrar por acueducto
- ✅ Búsqueda

### Movimientos
- ✅ Crear entrada
- ✅ Crear salida
- ✅ Crear transferencia
- ✅ Filtrar por tipo
- ✅ Ver historial

### Reportes
- ✅ Stock por sucursal
- ✅ Movimientos por período
- ✅ Alertas de stock bajo
- ✅ Estadísticas

### Administración
- ✅ CRUD de sucursales
- ✅ CRUD de acueductos
- ✅ CRUD de tuberías
- ✅ CRUD de equipos
- ✅ CRUD de usuarios
- ✅ CRUD de stock

---

## 🔄 Próximos Pasos

1. **Iniciar el servidor backend**
   ```bash
   python manage.py runserver
   ```

2. **Iniciar el servidor frontend**
   ```bash
   cd frontend
   npm start
   ```

3. **Acceder a la aplicación**
   ```
   http://localhost:3000
   ```

4. **Login con credenciales de prueba**
   ```
   Usuario: admin_test
   Contraseña: testpass123
   ```

5. **Explorar y probar funcionalidades**

---

## 📝 Notas Importantes

- Los datos son realistas para una hidroeléctrica operativa
- Todos los usuarios tienen contraseña: `testpass123`
- Las alertas están configuradas para stock bajo
- Los movimientos se pueden crear libremente
- La auditoría registra todas las operaciones
- Los permisos se validan según el rol del usuario

---

## ✅ Validación

Para verificar que los datos se cargaron correctamente:

```bash
# Ver cantidad de registros
python manage.py shell
>>> from inventario.models import *
>>> Sucursal.objects.count()  # Debe ser 3
>>> Acueducto.objects.count()  # Debe ser 7
>>> Tuberia.objects.count()  # Debe ser 6
>>> Equipo.objects.count()  # Debe ser 11
>>> StockTuberia.objects.count()  # Debe ser 7
>>> StockEquipo.objects.count()  # Debe ser 11
>>> AlertaStock.objects.count()  # Debe ser 4
>>> User.objects.count()  # Debe ser 3
```

---

**Estado**: ✅ Datos Cargados Exitosamente
**Fecha**: 2024
**Versión**: 1.0
