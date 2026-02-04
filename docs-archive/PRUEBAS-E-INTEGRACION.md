# Pruebas e Integración (Backend Refactor)

Este documento resume la estrategia de pruebas unitarias e integración para validar la nueva arquitectura.

## Estrategia
- Pruebas unitarias con `django.test.TestCase`.
- Datos comunes por clase con `setUpClass`.
- Cobertura de modelos, validaciones y efectos transversales.

## Cobertura Actual
- Modelos:
  - `Pipe`: creación, validaciones de longitud/tipo_uso/tipo_union.
  - `PumpAndMotor`: cálculo de kW, validaciones de potencia.
  - `Accessory`: dimensiones, presión, conexión.
  - `ChemicalProduct`: peligrosidad, caducidad.
- Stock:
  - Creación por producto; negativos prohibidos; unicidad `(producto, ubicacion)`.
- Movimientos:
  - ENTRADA suma en destino y crea auditoría SUCCESS.
  - SALIDA valida stock insuficiente y auditoría FAILED segura.
  - TRANSFER mueve stock entre ubicaciones y actualiza `FichaTecnicaMotor`.
  - AJUSTE suma/resta según ubicación provista.

## Ejecución
- Ejecutar solo inventario:
```powershell
cd backend
python manage.py test inventario
```
- Ejecutar conjunto de apps:
```powershell
cd backend
python manage.py test inventario geography institucion catalogo compras
```

## Buenas Prácticas
- Mantener datos de prueba consistentes y mínimos.
- Usar `full_clean()` para validar antes de `save()` cuando sea necesario.
- Limpiar auditorías FALLIDAS en pruebas negativas para evitar FK inválidos en teardown.
- Aislar efectos de `compras.OrdenCompra` creando usuarios (`creado_por`, `aprobado_por`).

## Próximos Pasos
- Añadir pruebas de API (DRF) para endpoints clave.
- Integrar cobertura con CI.
- Documentar métricas de cobertura y tiempos de ejecución.
