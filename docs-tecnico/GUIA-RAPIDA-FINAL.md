# Guía Rápida - MVP Completado

## 🚀 Inicio Rápido

### 1. Iniciar Backend
```bash
python manage.py runserver
```

### 2. Cargar Datos de Prueba
```bash
python manage.py seed_test_data
```

### 3. Acceder a la App
- URL: `http://localhost:3000`
- Usuario: `admin`
- Contraseña: `password`

---

## 📱 Navegación Principal

| Página | Acceso | Descripción |
|--------|--------|-------------|
| Dashboard | Inicio | Estadísticas y acciones rápidas |
| Stock | Menú | Gestión de inventario |
| Movimientos | Menú | Registro de movimientos |
| Alertas | Menú | Alertas de stock bajo |
| Administración | Menú (ADMIN) | Gestión de sucursales |
| Usuarios | Menú (ADMIN) | Gestión de usuarios |
| Reportes | Menú (ADMIN) | Reportes del sistema |

---

## ✨ Características Principales

### Dashboard
- Estadísticas en tiempo real
- Acciones rápidas (Entrada, Salida, Transferencia)
- Alertas de stock bajo
- Movimientos recientes
- Panel de administración (ADMIN)

### Stock
- Búsqueda y filtros
- Botones de acción (➕ ➖ ↔️)
- Modal de movimiento
- Cascada Sucursal → Acueducto
- Validación origen ≠ destino

### Movimientos
- Formulario completo
- Filtros por tipo
- Tabla de movimientos
- Validaciones

---

## 🔑 Validaciones Implementadas

1. **Origen ≠ Destino**: No permite transferencias al mismo acueducto
2. **Cantidad Válida**: Debe ser mayor a 0
3. **Acueducto Requerido**: En transferencias
4. **Artículo Requerido**: En todos los movimientos
5. **Stock Disponible**: Se muestra en el modal

---

## 🎨 Colores y Estados

| Color | Significado |
|-------|-------------|
| Verde | Éxito, Entrada |
| Rojo | Error, Salida |
| Azul | Info, Transferencia |
| Amarillo | Advertencia, Ajuste |

---

## 📊 Datos de Prueba

### Plantas Hidroeléctricas
- 5 plantas cargadas
- 10 acueductos/sistemas
- 7 tipos de tuberías
- 12 tipos de equipos

### Usuarios
- admin (ADMIN)
- operador1 (OPERADOR)
- operador2 (OPERADOR)

---

## 🧪 Pruebas

### Ejecutar Tests
```bash
python manage.py test inventario.tests
python manage.py test inventario.test_api
```

### Verificar Endpoints
```bash
curl http://localhost:8000/api/reportes/dashboard_stats/
curl http://localhost:8000/api/movimientos/
curl http://localhost:8000/api/reportes/alertas_stock_bajo/
```

---

## 📚 Documentación

- `DASHBOARD-COMPLETADO.md` - Detalles del dashboard
- `VERIFICACION-FINAL-MVP.md` - Checklist completo
- `RESUMEN-SESION-FINAL.md` - Resumen de cambios
- `VALIDACION-ACUEDUCTO-ORIGEN-DESTINO.md` - Validaciones
- `INTEGRACION-SWEETALERT2.md` - Alertas
- `MEJORA-SELECT2-SUCURSALES.md` - Cascada de selects

---

## ⚙️ Configuración

### Variables de Entorno
```
VITE_API_URL=http://localhost:8000
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Base de Datos
- SQLite (desarrollo)
- Migraciones automáticas

---

## 🔒 Seguridad

- Autenticación requerida
- Roles diferenciados
- Filtrado de datos por sucursal
- Validaciones en frontend y backend

---

## 💡 Tips

1. **Crear Movimiento desde Stock**: Usa los botones ➕ ➖ ↔️
2. **Transferencia entre Sucursales**: Selecciona sucursal primero
3. **Ver Alertas**: Haz clic en "Ver todas las alertas"
4. **Datos Recientes**: El dashboard se actualiza automáticamente
5. **Filtros**: Usa los filtros para encontrar movimientos específicos

---

## 🐛 Troubleshooting

### Error: "No se pudieron cargar las estadísticas"
- Verificar que el backend está corriendo
- Verificar que la URL de API es correcta
- Revisar la consola del navegador

### Error: "Acueducto destino no puede ser igual al origen"
- Selecciona un acueducto diferente
- Verifica que sea de otra sucursal

### Error: "Cantidad inválida"
- Ingresa un número mayor a 0
- Verifica que no exceda el stock disponible

---

## 📞 Contacto

Para soporte o preguntas, revisar la documentación en `docs-tecnico/`

---

**Status**: ✅ MVP COMPLETADO Y FUNCIONAL
