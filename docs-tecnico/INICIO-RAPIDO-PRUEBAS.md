# ⚡ Inicio Rápido - Pruebas Unitarias

## 1️⃣ Generar Datos de Prueba (2 minutos)

```bash
python manage.py seed_test_data
```

**Resultado**: Se crean 50+ registros realistas:
- 3 plantas hidroeléctricas
- 7 sistemas de bombeo/distribución
- 6 tipos de tuberías
- 11 equipos operativos
- 3 usuarios de prueba

## 2️⃣ Ejecutar Todas las Pruebas (5 minutos)

```bash
python manage.py test inventario -v 2
```

**Resultado**: 50+ pruebas ejecutadas
- ✅ Modelos validados
- ✅ API REST validada
- ✅ Lógica de movimientos validada
- ✅ Permisos por rol validados

## 3️⃣ Ejecutar Pruebas Específicas

### Solo Modelos
```bash
python manage.py test inventario.tests -v 2
```

### Solo API
```bash
python manage.py test inventario.test_api -v 2
```

### Solo Movimientos (Crítico)
```bash
python manage.py test inventario.tests.MovimientoInventarioTests -v 2
```

### Una Prueba Específica
```bash
python manage.py test inventario.tests.MovimientoInventarioTests.test_transferencia_entre_sucursales -v 2
```

## 4️⃣ Generar Reporte de Cobertura

```bash
# Instalar coverage (si no está instalado)
pip install coverage

# Ejecutar con cobertura
coverage run --source='inventario' manage.py test inventario
coverage report
coverage html

# Abrir reporte en navegador
# Linux/Mac: open htmlcov/index.html
# Windows: start htmlcov\index.html
```

## 5️⃣ Usar Scripts Automatizados

### Linux/Mac
```bash
chmod +x run_tests.sh
./run_tests.sh all          # Todas las pruebas
./run_tests.sh models       # Solo modelos
./run_tests.sh api          # Solo API
./run_tests.sh movements    # Solo movimientos
./run_tests.sh coverage     # Con cobertura
./run_tests.sh seed         # Generar datos
./run_tests.sh clean        # Limpiar BD
```

### Windows
```bash
run_tests.bat all
run_tests.bat models
run_tests.bat api
run_tests.bat movements
run_tests.bat coverage
run_tests.bat seed
run_tests.bat clean
```

## 6️⃣ Credenciales de Prueba

Después de ejecutar `seed_test_data`:

```
Admin:
  Usuario: admin_test
  Contraseña: testpass123
  Email: admin@test.com

Operador:
  Usuario: operador_test
  Contraseña: testpass123
  Email: operador@test.com
```

## 7️⃣ Validar Lógica de Movimientos

Las pruebas validan dos escenarios críticos:

### ✅ Transferencia Entre Sucursales
```
Planta A: 50 tuberías → 35 tuberías (disminuye)
Planta B: 0 tuberías → 15 tuberías (aumenta)
Total: 50 (se mantiene)
```

### ✅ Transferencia Mismo Acueducto
```
Sistema A: 50 tuberías → 40 tuberías (disminuye)
Sistema B: 0 tuberías → 10 tuberías (aumenta)
Total Planta: 50 (sin cambio - solo cambio de ubicación)
```

## 📊 Qué se Prueba

| Componente | Pruebas | Estado |
|-----------|---------|--------|
| Tuberías | 3 | ✅ |
| Equipos | 3 | ✅ |
| Stock | 3 | ✅ |
| Movimientos | 8 | ✅ |
| Alertas | 3 | ✅ |
| Serializers | 6 | ✅ |
| API Tuberías | 5 | ✅ |
| API Equipos | 3 | ✅ |
| API Stock | 4 | ✅ |
| API Movimientos | 7 | ✅ |
| API Usuarios | 4 | ✅ |
| API Auditoría | 2 | ✅ |
| API Reportes | 3 | ✅ |
| **TOTAL** | **50+** | **✅** |

## 🔍 Verificar Permisos

Las pruebas validan que:

```
✅ Admin puede crear tuberías
❌ Operador NO puede crear tuberías (403)

✅ Admin puede listar usuarios
❌ Operador NO puede listar usuarios (403)

✅ Ambos pueden crear movimientos
✅ Ambos pueden listar stock
```

## 🐛 Solucionar Problemas

### Error: "No module named 'inventario'"
```bash
# Asegúrate de estar en el directorio raíz del proyecto
cd /ruta/al/proyecto
python manage.py test inventario
```

### Error: "Database connection refused"
```bash
# Asegúrate de que la BD está disponible
python manage.py migrate
python manage.py test inventario
```

### Error: "ModuleNotFoundError: No module named 'coverage'"
```bash
pip install coverage
```

## 📚 Documentación Completa

Para más detalles, ver: `docs/10-PRUEBAS-UNITARIAS.md`

## ✨ Resumen

1. **Generar datos**: `python manage.py seed_test_data`
2. **Ejecutar pruebas**: `python manage.py test inventario -v 2`
3. **Ver cobertura**: `coverage report`
4. **Usar credenciales**: admin_test / testpass123

¡Listo! 🎉
