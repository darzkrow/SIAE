# 🔄 Guía de Migración: Sistema Antiguo → Sistema Refactorizado

## 📋 Resumen de Cambios

### Modelos Antiguos → Nuevos

| Antiguo | Nuevo | Cambios Principales |
|---------|-------|---------------------|
| `Tuberia` | `Pipe` | + Material PEAD/Cobre, + Tipo unión, + Espesor pared |
| `Equipo` | `PumpAndMotor` | + Tipo equipo, + Espec. hidráulicas, + Curva |
| - | `ChemicalProduct` | **NUEVO** - Productos químicos |
| - | `Accessory` | **NUEVO** - Accesorios |
| `StockTuberia` | `StockPipe` | + Metros totales calculados |
| `StockEquipo` | `StockPumpAndMotor` | + Estado operativo |
| `Categoria` | `Category` | + Código SKU, + Orden |
| - | `UnitOfMeasure` | **NUEVO** - Unidades normalizadas |
| - | `Supplier` | **NUEVO** - Proveedores |

---

## 🚀 Pasos de Migración

### Fase 1: Preparación (Sin downtime)

#### 1.1 Backup de Base de Datos
```bash
# PostgreSQL
pg_dump -U gsih_user -d gsih_inventario > backup_pre_migration.sql

# O con Docker
docker-compose exec db pg_dump -U gsih_user gsih_inventario > backup_pre_migration.sql
```

#### 1.2 Renombrar models.py Original
```bash
cd inventario
mv models.py models_legacy.py
cp models_refactored_consolidated.py models.py
```

#### 1.3 Crear Migraciones
```bash
python manage.py makemigrations inventario
# Revisar archivo de migración generado
```

---

### Fase 2: Migración de Datos

#### 2.1 Crear Datos Auxiliares

**Script**: `create_initial_data.py`

```python
from inventario.models import Category, UnitOfMeasure, Supplier

# Categorías
categorias = [
    {'nombre': 'Productos Químicos', 'codigo': 'QUI', 'orden': 1},
    {'nombre': 'Tuberías', 'codigo': 'TUB', 'orden': 2},
    {'nombre': 'Bombas y Motores', 'codigo': 'BOM', 'orden': 3},
    {'nombre': 'Accesorios', 'codigo': 'ACC', 'orden': 4},
]

for cat_data in categorias:
    Category.objects.get_or_create(
        codigo=cat_data['codigo'],
        defaults=cat_data
    )

# Unidades de Medida
unidades = [
    {'nombre': 'Metro', 'simbolo': 'm', 'tipo': 'LONGITUD'},
    {'nombre': 'Litro', 'simbolo': 'L', 'tipo': 'VOLUMEN'},
    {'nombre': 'Kilogramo', 'simbolo': 'kg', 'tipo': 'PESO'},
    {'nombre': 'Unidad', 'simbolo': 'un', 'tipo': 'UNIDAD'},
    {'nombre': 'Saco', 'simbolo': 'saco', 'tipo': 'UNIDAD'},
]

for unidad_data in unidades:
    UnitOfMeasure.objects.get_or_create(
        simbolo=unidad_data['simbolo'],
        defaults=unidad_data
    )

# Proveedor genérico
Supplier.objects.get_or_create(
    codigo='GEN',
    defaults={
        'nombre': 'Proveedor General',
        'rif': 'J-00000000-0'
    }
)
```

#### 2.2 Migrar Tuberías → Pipe

**Script**: `migrate_tuberias.py`

```python
from inventario.models_legacy import Tuberia as TuberiaLegacy, StockTuberia as StockTuberiaLegacy
from inventario.models import Pipe, StockPipe, Category, UnitOfMeasure, Supplier
from decimal import Decimal

# Obtener referencias
categoria_tub = Category.objects.get(codigo='TUB')
unidad_unidad = UnitOfMeasure.objects.get(simbolo='un')
proveedor_gen = Supplier.objects.get(codigo='GEN')

# Migrar tuberías
for tuberia_old in TuberiaLegacy.objects.all():
    # Mapear material antiguo a nuevo
    material_map = {
        'PVC': 'PVC',
        'HIERRO': 'HIERRO_DUCTIL',
        'CEMENTO': 'CEMENTO',
        'OTRO': 'OTRO'
    }
    
    pipe_new = Pipe.objects.create(
        nombre=tuberia_old.nombre,
        descripcion=tuberia_old.descripcion,
        categoria=categoria_tub,
        unidad_medida=unidad_unidad,
        proveedor=proveedor_gen,
        stock_actual=Decimal('0'),  # Se migra después
        stock_minimo=Decimal('10'),  # Valor por defecto
        precio_unitario=Decimal('0'),  # Actualizar manualmente
        
        # Campos específicos
        material=material_map.get(tuberia_old.material, 'OTRO'),
        diametro_nominal=Decimal(str(tuberia_old.diametro_nominal_mm)),
        unidad_diametro='MM',
        presion_nominal='PN10',  # Valor por defecto
        longitud_unitaria=tuberia_old.longitud_m,
        tipo_union='SOLDABLE',  # Valor por defecto
        tipo_uso=tuberia_old.tipo_uso
    )
    
    print(f"Migrada: {pipe_new.sku} - {pipe_new.nombre}")
    
    # Migrar stocks
    for stock_old in StockTuberiaLegacy.objects.filter(tuberia=tuberia_old):
        stock_new = StockPipe.objects.create(
            producto=pipe_new,
            acueducto=stock_old.acueducto,
            cantidad=stock_old.cantidad,
            ubicacion_fisica='Migrado desde sistema antiguo'
        )
        print(f"  Stock migrado: {stock_new.cantidad} en {stock_old.acueducto}")

print(f"\nTotal tuberías migradas: {Pipe.objects.count()}")
```

#### 2.3 Migrar Equipos → PumpAndMotor

**Script**: `migrate_equipos.py`

```python
from inventario.models_legacy import Equipo as EquipoLegacy, StockEquipo as StockEquipoLegacy
from inventario.models import PumpAndMotor, StockPumpAndMotor, Category, UnitOfMeasure, Supplier
from decimal import Decimal

categoria_bom = Category.objects.get(codigo='BOM')
unidad_unidad = UnitOfMeasure.objects.get(simbolo='un')
proveedor_gen = Supplier.objects.get(codigo='GEN')

for equipo_old in EquipoLegacy.objects.all():
    pump_new = PumpAndMotor.objects.create(
        nombre=equipo_old.nombre,
        descripcion=equipo_old.descripcion,
        categoria=categoria_bom,
        unidad_medida=unidad_unidad,
        proveedor=proveedor_gen,
        stock_actual=Decimal('0'),
        stock_minimo=Decimal('1'),
        precio_unitario=Decimal('0'),
        
        # Campos específicos
        tipo_equipo='BOMBA_CENTRIFUGA',  # Valor por defecto
        marca=equipo_old.marca or 'Sin marca',
        modelo=equipo_old.modelo or 'Sin modelo',
        numero_serie=equipo_old.numero_serie,
        potencia_hp=equipo_old.potencia_hp or Decimal('1'),
        voltaje=220,  # Valor por defecto
        fases='TRIFASICO',
        frecuencia=60
    )
    
    print(f"Migrado: {pump_new.sku} - {pump_new.nombre}")
    
    # Migrar stocks
    for stock_old in StockEquipoLegacy.objects.filter(equipo=equipo_old):
        stock_new = StockPumpAndMotor.objects.create(
            producto=pump_new,
            acueducto=stock_old.acueducto,
            cantidad=int(stock_old.cantidad),
            estado_operativo='OPERATIVO',
            ubicacion_fisica='Migrado desde sistema antiguo'
        )

print(f"\nTotal equipos migrados: {PumpAndMotor.objects.count()}")
```

---

### Fase 3: Actualizar Código

#### 3.1 Actualizar serializers.py
```bash
# Descomentar imports en serializers_refactored.py
# Remover serializers antiguos de serializers.py
```

#### 3.2 Actualizar views.py
```bash
# Descomentar imports y querysets en views_refactored.py
# Actualizar o deprecar views antiguos
```

#### 3.3 Actualizar urls.py
```python
# En inventario/urls.py, agregar:
from inventario.urls_refactored import router_refactored

urlpatterns = [
    # Rutas existentes (deprecadas pero funcionales)
    path('api/', include(router.urls)),
    
    # Nuevas rutas (recomendadas)
    path('api/v2/', include(router_refactored.urls)),
]
```

---

### Fase 4: Verificación

#### 4.1 Verificar Migración
```python
# Script de verificación
from inventario.models import Pipe, PumpAndMotor, StockPipe, StockPumpAndMotor

print("=== VERIFICACIÓN DE MIGRACIÓN ===")
print(f"Tuberías (Pipe): {Pipe.objects.count()}")
print(f"Bombas/Motores: {PumpAndMotor.objects.count()}")
print(f"Stocks Tuberías: {StockPipe.objects.count()}")
print(f"Stocks Bombas: {StockPumpAndMotor.objects.count()}")

# Verificar SKU generados
print("\n=== PRIMEROS 5 SKUs ===")
for pipe in Pipe.objects.all()[:5]:
    print(f"{pipe.sku}: {pipe.nombre}")
```

#### 4.2 Probar Endpoints
```bash
# Obtener token
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Listar tuberías nuevas
curl http://localhost:8000/api/v2/pipes/ \
  -H "Authorization: Token YOUR_TOKEN"

# Crear producto químico
curl -X POST http://localhost:8000/api/v2/chemicals/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Cloro 70%",
    "categoria": 1,
    "unidad_medida": 3,
    "proveedor": 1,
    "es_peligroso": true,
    "nivel_peligrosidad": "ALTO",
    "presentacion": "SACO"
  }'
```

---

## ⚠️ Consideraciones Importantes

### Downtime
- **Estimado**: 30-60 minutos
- **Recomendación**: Realizar en horario de bajo tráfico

### Rollback Plan
```bash
# Si algo sale mal, restaurar backup
psql -U gsih_user -d gsih_inventario < backup_pre_migration.sql

# Revertir código
cd inventario
mv models.py models_refactored.py
mv models_legacy.py models.py
```

### Datos Incompatibles
- **Tuberías sin diámetro**: Asignar valor por defecto
- **Equipos sin número de serie**: Generar automáticamente
- **Campos nulos**: Usar valores por defecto documentados

---

## 📊 Checklist de Migración

- [ ] Backup de base de datos
- [ ] Crear datos auxiliares (Category, UnitOfMeasure, Supplier)
- [ ] Migrar Tuberías → Pipe
- [ ] Migrar Equipos → PumpAndMotor
- [ ] Migrar Stocks
- [ ] Actualizar imports en serializers/views
- [ ] Actualizar URLs
- [ ] Ejecutar tests
- [ ] Verificar endpoints API
- [ ] Actualizar frontend (si aplica)
- [ ] Documentar cambios

---

## 🎯 Después de la Migración

1. **Actualizar precios**: Los precios migran en 0, actualizar manualmente
2. **Completar proveedores**: Cambiar de "Proveedor General" al real
3. **Ajustar stocks mínimos**: Revisar valores por defecto
4. **Agregar químicos**: Crear productos químicos necesarios
5. **Agregar accesorios**: Crear accesorios (válvulas, codos, etc)
6. **Deprecar API antigua**: Después de validación, remover rutas antiguas

---

## 📞 Soporte

En caso de problemas durante la migración, consultar:
- `docs/GUIA_MODELOS_REFACTORIZADOS.md`
- Logs de Django: `logs/django.log`
- Contactar al equipo de desarrollo
