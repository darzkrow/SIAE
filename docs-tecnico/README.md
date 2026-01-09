# Inventario (demo)

Este repositorio contiene una app Django llamada `inventario` diseñada para gestionar el stock
de materiales críticos en una estructura organizacional jerárquica: la Organización Central
(`Hidroven`) > Sucursales (16 entidades) > Acueductos (múltiples por sucursal).

Resumen de modelos y responsabilidades
- `OrganizacionCentral`: entidad única (ej. Hidroven). Campos: `nombre`, `rif`.
- `Sucursal`: 16 entidades regionales. Campos: `nombre`, `organizacion_central` (FK).
- `Acueducto`: unidad de inventario granular. Campos: `nombre`, `sucursal` (FK).
- `Categoria`: clasificación general de artículos (e.g., Tuberías, Equipos).
- `ArticuloBase` (abstract): datos comunes `nombre`, `descripcion`, `categoria`.
- `Tuberia` (hereda `ArticuloBase`): `material`, `tipo_uso`, `diametro_nominal_mm`, `longitud_m`.
- `Equipo` (hereda `ArticuloBase`): `marca`, `modelo`, `potencia_hp`, `numero_serie` (único).

Control de Stock (modelo final)
- `StockTuberia`: cantidad de una `Tuberia` en un `Acueducto`.
- `StockEquipo`: cantidad de un `Equipo` en un `Acueducto`.

Ambos modelos aplican:
- Restricción a nivel de base de datos: `cantidad >= 0` (CheckConstraint).
- Validación al guardar (`save`) que impide asignar cantidades negativas (lanza `ValidationError`).

Movimientos y trazabilidad
- `MovimientoInventario`: registra entradas, salidas, transferencias y ajustes. Contiene FKs opcionales a `Tuberia` o `Equipo` (exactamente uno debe estar presente), `acueducto_origen`, `acueducto_destino`, `tipo_movimiento`, `cantidad`, `fecha_movimiento` y `razon`.
- Validaciones principales:
	- Salida/Transferencia requiere stock suficiente en el origen; si no hay stock o es insuficiente, el movimiento falla y se lanza `ValidationError`.
	- Transferencia requiere tanto origen como destino.
	- Entrada requiere destino.
- Concurrencia y atomicidad:
	- Las actualizaciones sobre `StockTuberia`/`StockEquipo` se hacen dentro de `transaction.atomic()` y usando `select_for_update()` y `F()` para evitar condiciones de carrera.

Auditoría de movimientos
- `InventoryAudit`: modelo que registra cada intento de movimiento con estado: `PENDING`, `SUCCESS`, `FAILED`.
- `MovimientoInventario.save()` crea una entrada de auditoría ligada al movimiento (`PENDING`) y la actualiza a `SUCCESS` o `FAILED` con un mensaje explicativo según el resultado. En errores de validación se guarda la razón antes de propagar la excepción.

Seed y utilidades
- `management/commands/seed_inventario.py`: comando idempotente que crea:
	- `OrganizacionCentral` "Hidroven";
	- 16 `Sucursal` (incluye `Hidrocapital`);
	- 7 `Acueducto` para `Hidrocapital` y 2 para cada otra sucursal;
	- Categorías de ejemplo y un artículo `Tuberia` y `Equipo` de muestra.

Diagrama de flujo (mermaid)

```mermaid
flowchart TD
	A[Inicio: Crear Movimiento] --> B{¿Artículo especificado?}
	B -- No --> BF[Crear Audit FAILED: artículo no especificado]
	B -- Sí --> C[Guardar Movimiento (PENDING)]
	C --> D{Tipo: ENTRADA / SALIDA / TRANSFER / AJUSTE}
	D -->|ENTRADA| E[Verificar destino]
	E -->|no destino| EF[Audit FAILED: destino requerido]
	E -->|ok| EG[Lock stock destino / crear si no existe]
	EG --> EH[Incrementar stock con F()]
	EH --> EI[Audit SUCCESS]

	D -->|SALIDA| F[Verificar origen]
	F -->|no origen| FF[Audit FAILED: origen requerido]
	F -->|ok| FG[Lock stock origen]
	FG --> FH{stock >= cantidad?}
	FH -->|no| FI[Audit FAILED: stock insuficiente]
	FH -->|si| FJ[Decrementar stock con F()]
	FJ --> FK[Audit SUCCESS]

	D -->|TRANSFER| T1[Requerir origen y destino]
	T1 -->|faltan| TF[Audit FAILED]
	T1 -->|ok| T2[Lock origen & verificar stock]
	T2 -->|insuficiente| TI[Audit FAILED]
	T2 -->|ok| T3[Decrementar origen; Incrementar destino]
	T3 --> TJ[Audit SUCCESS]

	D -->|AJUSTE| A1[Aplicar ajuste en origen o destino]
	A1 --> A2[Lock fila y aplicar suma]
	A2 --> A3[Audit SUCCESS]

	subgraph Auditar
		BF
		EF
		FI
		FF
		TF
	end
```

Nota: el diagrama muestra el flujo lógico principal y los puntos donde se generan auditorías en caso de fallo.

Instalación y ejecución rápida
1) Crear y activar entorno virtual e instalar Django:

```bash
python -m venv .venv
source .venv/bin/activate
pip install django
```

2) Migraciones y seed:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_inventario
```

3) Crear superusuario y ejecutar servidor:

```bash
python manage.py createsuperuser
python manage.py runserver
```

4) Probar un movimiento (ejemplo en shell):

```bash
python manage.py shell
>>> from inventario.models import Tuberia, MovimientoInventario, Acueducto
>>> t = Tuberia.objects.first()
>>> dest = Acueducto.objects.first()
>>> m = MovimientoInventario(tuberia=t, acueducto_destino=dest, tipo_movimiento='ENTRADA', cantidad=5, razon='Ingreso inicial')
>>> m.save()
```

Consideraciones y mejoras futuras
- Añadir control de usuarios y permisos para aprobar movimientos que cambien stock crítico.
- Añadir notificaciones (email/SMS) para detección de stock crítico bajo umbral.
- Implementar pruebas unitarias automáticas que verifiquen flujos de ENTRADA/SALIDA/TRANSFER y que la auditoría registre correctamente los fallos.

Alertas y notificaciones (implementado)
-------------------------------------
Se añadió soporte para alertas de stock y notificaciones:

- `AlertaStock`: define un umbral para un artículo (`Tuberia` o `Equipo`) en un `Acueducto`. Campos clave: `umbral_minimo`, `activo`.
- `Notification`: registro de notificaciones generadas cuando el stock está por debajo del umbral.

Comando para revisar alertas
- `python manage.py check_stock_alerts` — recorre todas las `AlertaStock` activas y, si el `Stock` correspondiente está por debajo o igual al umbral, crea una `Notification` y, opcionalmente, envía un email.

Evitar duplicados
- El comando evita crear notificaciones repetidas con menos de 24 horas entre ellas para la misma alerta.

Configuración de envío de email
- Si en `config/settings.py` defines `STOCK_ALERT_EMAILS = ['ops@example.com']` y `DEFAULT_FROM_EMAIL`, el comando intentará enviar un email cuando cree una notificación.

Programar ejecución periódica (cron)
- Ejemplo de entrada de `crontab` para ejecutar cada 30 minutos (ajusta rutas y entorno):

```cron
*/30 * * * * /home/usuario/.venv/bin/python /home/usuario/Escritorio/GSIH/manage.py check_stock_alerts
```

O usar `systemd` timers o herramientas como `django-crontab` o `celery-beat` para ejecución más avanzada.




# GSIH
