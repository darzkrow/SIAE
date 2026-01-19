# 📚 Guía de Uso: Sistema de Inventario Refactorizado

Esta guía refleja la arquitectura refactorizada del backend (2026). Asegúrate de crear las entidades base (catálogos) antes de instanciar productos.

Prerequisitos mínimos:
- `CategoriaProducto` (ej.: TUB, BOM, ACC, QUI)
- `UnitOfMeasure` (ej.: m, kg, u)
- `Supplier` (proveedor)
- `Marca` (para `PumpAndMotor`)

## 🎯 Descripción General

Sistema de inventario robusto para empresas de Agua Potable y Saneamiento, implementado con **Abstract Base Classes** para máximo rendimiento.

---

## 📦 Modelos Disponibles

### Modelos Auxiliares

#### 1. **Category** (Categorías)
```python
categoria = Category.objects.create(
    nombre='Productos Químicos',
    codigo='QUI',
    descripcion='Químicos para tratamiento de agua',
    activo=True,
    orden=1
)
```

#### 2. **UnitOfMeasure** (Unidades de Medida)
```python
unidad_kg = UnitOfMeasure.objects.create(
    nombre='Kilogramo',
    simbolo='kg',
    tipo='PESO',
    activo=True
)
```

#### 3. **Supplier** (Proveedores)
```python
proveedor = Supplier.objects.create(
    nombre='Químicos del Caribe C.A.',
    rif='J-123456789',
    codigo='QDC',
    contacto_nombre='Juan Pérez',
    telefono='0212-1234567',
    email='ventas@quimicosdelcaribe.com',
    activo=True
)
```

---

### Modelos de Productos

#### 1. **ChemicalProduct** (Productos Químicos)

```python
cloro = ChemicalProduct.objects.create(
    # Campos base
    nombre='Hipoclorito de Calcio 70%',
    descripcion='Hipoclorito de calcio granular para desinfección',
    categoria=categoria_quimicos,
    unidad_medida=unidad_kg,
    stock_actual=Decimal('500.00'),
    stock_minimo=Decimal('100.00'),
    precio_unitario=Decimal('25.50'),
    proveedor=proveedor_quimicos,
    
    # Campos específicos de químicos
    es_peligroso=True,
    nivel_peligrosidad='ALTO',
    fecha_caducidad='2025-12-31',
    concentracion=Decimal('70.00'),
    unidad_concentracion='PORCENTAJE',
    presentacion='SACO',
    peso_neto=Decimal('50.00'),
    numero_un='UN2880'
)

# Métodos disponibles
print(cloro.sku)  # Auto-generado: QUI-CHE-0001
print(cloro.get_stock_status())  # 'NORMAL', 'BAJO', 'CRITICO', 'AGOTADO'
print(cloro.is_expired())  # False
print(cloro.days_until_expiration())  # 365
```

#### 2. **Pipe** (Tuberías)

```python
tuberia = Pipe.objects.create(
    nombre='Tubería PVC Sanitaria 110mm PN10',
    descripcion='Tubería PVC para agua potable',
    categoria=categoria_tuberias,
    unidad_medida=unidad_unidad,
    stock_actual=Decimal('100'),
    stock_minimo=Decimal('20'),
    precio_unitario=Decimal('45.00'),
    proveedor=proveedor_tuberias,
    
    # Campos específicos de tuberías
    material='PVC',
    diametro_nominal=Decimal('110'),
    unidad_diametro='MM',
    presion_nominal='PN10',
    longitud_unitaria=Decimal('6.00'),
    tipo_union='SOLDABLE',
    tipo_uso='POTABLE',
    espesor_pared=Decimal('2.7')
)

# Presión en PSI se calcula automáticamente
print(tuberia.presion_psi)  # 145.038
print(tuberia.get_diametro_display())  # "110 Milímetros (mm)"
```

#### 3. **PumpAndMotor** (Bombas y Motores)

```python
from catalogo.models import Marca
marca_pedrollo = Marca.objects.create(nombre='Pedrollo')

bomba = PumpAndMotor.objects.create(
    nombre='Bomba Centrífuga 5HP',
    descripcion='Bomba para sistema de distribución',
    categoria=categoria_bombas,
    unidad_medida=unidad_unidad,
    stock_actual=Decimal('3'),
    stock_minimo=Decimal('1'),
    precio_unitario=Decimal('1250.00'),
    proveedor=proveedor_equipos,
    
    # Campos específicos
    tipo_equipo='BOMBA_CENTRIFUGA',
    marca=marca_pedrollo,
    modelo='CPm-200',
    numero_serie='PED-2024-12345',
    
    # Eléctricos
    potencia_hp=Decimal('5.0'),
    voltaje=220,
    fases='TRIFASICO',
    frecuencia=60,
    amperaje=Decimal('12.5'),
    
    # Hidráulicos
    caudal_maximo=Decimal('15.0'),
    unidad_caudal='L/S',
    altura_dinamica=Decimal('45.0'),
    eficiencia=Decimal('78.5')
)

# Potencia en kW se calcula automáticamente
print(bomba.potencia_kw)  # 3.7285
print(bomba.get_potencia_display())  # "5.0 HP (3.73 kW)"
```

#### 4. **Accessory** (Accesorios)

```python
# Válvula
valvula = Accessory.objects.create(
    nombre='Válvula de Compuerta 4" Bridada',
    categoria=categoria_accesorios,
    unidad_medida=unidad_unidad,
    stock_actual=Decimal('8'),
    stock_minimo=Decimal('2'),
    precio_unitario=Decimal('185.00'),
    proveedor=proveedor_accesorios,
    
    tipo_accesorio='VALVULA',
    subtipo='COMPUERTA',
    diametro_entrada=Decimal('4'),
    unidad_diametro='PULGADAS',
    tipo_conexion='BRIDADA',
    presion_trabajo='PN16',
    material='HIERRO'
)

# Codo
codo = Accessory.objects.create(
    nombre='Codo PVC 90° 2"',
    categoria=categoria_accesorios,
    unidad_medida=unidad_unidad,
    stock_actual=Decimal('50'),
    stock_minimo=Decimal('10'),
    precio_unitario=Decimal('12.50'),
    proveedor=proveedor_accesorios,
    
    tipo_accesorio='CODO',
    diametro_entrada=Decimal('2'),
    unidad_diametro='PULGADAS',
    tipo_conexion='SOLDABLE',
    angulo=90,
    presion_trabajo='PN10',
    material='PVC'
)

print(codo.get_dimension_display())  # "2 Pulgadas"
```

---

### Modelos de Stock

Antes de crear stock, define una `Ubicacion` (app `geography`):
```python
from geography.models import Ubicacion
ubicacion_principal = Ubicacion.objects.create(
    nombre='Almacén Central', acueducto=acueducto_central, tipo='ALMACEN'
)
```

#### StockChemical
```python
stock_cloro = StockChemical.objects.create(
    producto=cloro,
    ubicacion=ubicacion_principal,
    cantidad=Decimal('250.000'),
    lote='LOTE-2024-001',
    fecha_vencimiento='2025-12-31'
)
```

#### StockPipe
```python
stock_tuberia = StockPipe.objects.create(
    producto=tuberia,
    ubicacion=ubicacion_principal,
    cantidad=Decimal('50.000')  # 50 tubos
)
# metros_totales se calcula automáticamente: 50 * 6.0 = 300m
print(stock_tuberia.metros_totales)  # 300.00
```

#### StockPumpAndMotor
```python
stock_bomba = StockPumpAndMotor.objects.create(
    producto=bomba,
    ubicacion=ubicacion_principal,
    cantidad=2,
    estado_operativo='OPERATIVO'
)
```

#### StockAccessory
```python
stock_valvula = StockAccessory.objects.create(
    producto=valvula,
    ubicacion=ubicacion_principal,
    cantidad=Decimal('4.000')
)
```

---

---

## 📋 Valores válidos (choices)

### Pipe
- Material: PVC, PEAD, ACERO, HIERRO_DUCTIL, CEMENTO, COBRE, OTRO
- UnidadDiametro: PULGADAS, MM
- PresionNominal: PN6, PN10, PN16, PN20, PN25, SDR11, SDR17, SDR21, SDR26, SDR41
- TipoUnion: SOLDABLE, ROSCADA, BRIDADA, CAMPANA, FUSION
- TipoUso: POTABLE, SERVIDAS, RIEGO, PLUVIAL, INDUSTRIAL

### PumpAndMotor
- TipoEquipo: BOMBA_CENTRIFUGA, BOMBA_SUMERGIBLE, BOMBA_PERIFERICA, BOMBA_TURBINA, MOTOR_ELECTRICO, VARIADOR
- Fases: MONOFASICO, TRIFASICO
- unidad_caudal: L/S, M3/H

### Accessory
- TipoAccesorio: VALVULA, CODO, TEE, REDUCCION, TAPON, BRIDA, UNION, COLLAR, ADAPTADOR
- SubtipoValvula: BOLA, COMPUERTA, RETENCION, MARIPOSA, GLOBO, ALIVIO, FLOTADOR
- TipoConexion: BRIDADA, ROSCADA, SOLDABLE, CAMPANA, RAPIDA
- unidad_diametro: PULGADAS, MM
- presion_trabajo: PN6, PN10, PN16, PN20, PN25, 150LB, 300LB

### ChemicalProduct
- NivelPeligrosidad: BAJO, MEDIO, ALTO, MUY_ALTO
- TipoPresentacion: SACO, TAMBOR, GRANEL, GALON, CILINDRO, OTRO
- UnidadConcentracion: PORCENTAJE, G_L, MG_L, PPM

---

## 🔍 Consultas Comunes

### Productos con stock bajo
```python
# Químicos peligrosos con stock crítico
quimicos_criticos = ChemicalProduct.objects.filter(
    es_peligroso=True,
    stock_actual__lte=models.F('stock_minimo')
)

# Tuberías de un material específico
tuberias_pvc = Pipe.objects.filter(material='PVC', activo=True)

# Bombas por rango de potencia
bombas_5hp = PumpAndMotor.objects.filter(
    tipo_equipo='BOMBA_CENTRIFUGA',
    potencia_hp__gte=Decimal('5.0'),
    potencia_hp__lte=Decimal('10.0')
)
```

### Stock por acueducto
```python
# Todo el stock de químicos en un acueducto
stocks = StockChemical.objects.filter(
    acueducto=acueducto_central
).select_related('producto', 'producto__categoria')

for stock in stocks:
    print(f"{stock.producto.nombre}: {stock.cantidad} {stock.producto.unidad_medida.simbolo}")
```

### Productos próximos a vencer
```python
from datetime import timedelta

proximos_vencer = ChemicalProduct.objects.filter(
    fecha_caducidad__lte=timezone.now().date() + timedelta(days=30),
    activo=True
)
```

---

## 📊 Reportes Útiles

### Valor del Inventario
```python
from django.db.models import Sum, F

valor_total = ChemicalProduct.objects.aggregate(
    valor=Sum(F('stock_actual') * F('precio_unitario'))
)
```

### Stock por categoría
```python
from django.db.models import Count

stats_categorias = Category.objects.annotate(
    total_productos_quimicos=Count('chemicalproduct_productos'),
    total_tuberias=Count('pipe_productos'),
    total_bombas=Count('pumpandmotor_productos'),
    total_accesorios=Count('accessory_productos')
)
```

---

## ⚡ Performance Tips

### Optimizar consultas
```python
# ✅ BUENO: Con select_related
productos = ChemicalProduct.objects.select_related(
    'categoria', 'unidad_medida', 'proveedor'
).all()

# ❌ MALO: Sin optimización (genera N+1 queries)
productos = ChemicalProduct.objects.all()
```

### Bulk operations
```python
# Crear múltiples productos eficientemente
productos = [
    ChemicalProduct(nombre=f"Producto {i}", ...)
    for i in range(100)
]
ChemicalProduct.objects.bulk_create(productos)
```

---

## 🔧 Métodos Útiles

### ProductBase (todos los productos heredan)
- `get_stock_status()`: Retorna 'AGOTADO', 'CRITICO', 'BAJO', 'NORMAL'
- `is_below_minimum()`: True si stock < mínimo
- `get_stock_percentage()`: Porcentaje de stock vs mínimo
- `generate_sku()`: Genera SKU automático
- `__str__()`: Representación legible

### ChemicalProduct
- `is_expired()`: True si ha vencido
- `days_until_expiration()`: Días hasta vencimiento

### Pipe
- `get_diametro_display()`: Diámetro formateado con unidad

### PumpAndMotor
- `get_potencia_display()`: Potencia en HP y kW

### Accessory
- `get_dimension_display()`: Dimensiones formateadas

---

## 🎯 Validaciones Automáticas

- Stock no puede ser negativo
- Precios no pueden ser negativos
- SKU único y auto-generado
- Químicos peligrosos requieren nivel de peligrosidad
- Reducciones requieren diámetro de salida
- Codos requieren ángulo
- Conversión automática PN a PSI
- Conversión automática HP a kW
- Cálculo automático de metros totales en tuberías

---

## 📝 Notas Importantes

1. **SKU se genera automáticamente** si no se proporciona
2. **No usar FloatField** para precios - siempre DecimalField
3. **Stock usa 3 decimales** para precisión
4. **Precios usan 2 decimales**
5. **Todos los modelos tienen timestamps** (creado_en, actualizado_en)
6. **Índices optimizados** para consultas frecuentes

---

## 🚀 Próximos Pasos

1. Ejecutar migraciones: `python manage.py makemigrations`
2. Aplicar migraciones: `python manage.py migrate`
3. Crear datos iniciales (fixtures o admin)
4. Crear serializers para API
5. Actualizar views y URLs
