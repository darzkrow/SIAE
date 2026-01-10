# 📖 Manual de Uso - Sistema GSIH Inventario

Bienvenido al Manual de Uso del **Sistema de Gestión de Inventario de Activos Hidrológicos (GSIH)**. Este documento le guiará a través de las funcionalidades principales del sistema para una gestión eficiente de activos (tuberías, equipos, químicos y accesorios).

---

## 1. Acceso al Sistema (Login)

Para ingresar al sistema:
1. Ingrese su **Nombre de Usuario**.
2. Ingrese su **Contraseña**.
3. Haga clic en **"Iniciar Sesión"**.

> [!NOTE]
> Su rol (ADMIN u OPERADOR) determinará a qué secciones del sistema tiene acceso. Los administradores tienen acceso total, mientras que los operadores están limitados a la gestión de su acueducto asignado.

---

## 2. Panel de Control (Dashboard)

Al ingresar, verá el Dashboard principal que ofrece una visión general del sistema:
- **Resumen de Stock**: Cantidad total de tuberías y equipos.
- **Alertas Activas**: Visualización rápida de artículos con stock por debajo del mínimo.
- **Acciones Rápidas**: Botones para crear Entradas, Salidas o Transferencias de forma veloz.
- **Movimientos Recientes**: Tabla con los últimos registros realizados en el sistema.

---

## 3. Catálogo de Artículos

Ubicado en el menú **"Artículos"**, aquí se gestiona la definición de los productos.

### Tipos de Artículos
El sistema divide los artículos en cuatro categorías:
- **Químicos**: Productos para tratamiento (cloro, sulfatos, etc.).
- **Tuberías**: Gestión por material y diámetro.
- **Bombas/Motores**: Gestión por potencia (HP), marca y modelo.
- **Accesorios**: Válvulas, codos, uniones, etc.

### Acciones Disponibles (Solo Administradores)
- **Nuevo Artículo**: Botón azul superior para registrar un nuevo producto en la categoría activa.
- **Editar**: Ícono de lápiz en la tabla para modificar datos.
- **Eliminar**: Ícono de papelera para dar de baja un artículo.

---

## 4. Movimientos de Inventario

Esta es la sección más crítica para mantener el inventario actualizado.

### Registrar un Movimiento
1. Vaya a la sección **"Movimientos"**.
2. Haga clic en **"+ Nuevo Movimiento"**.
3. Complete los campos obligatorios:
   - **Tipo**: Entrada, Salida, Transferencia o Ajuste.
   - **Producto**: Busque y seleccione el artículo específico.
   - **Cantidad**: Número de unidades a mover.
   - **Origen/Destino**: Seleccione los acueductos involucrados según el tipo de movimiento.
   - **Razón**: Breve explicación del movimiento (ej: "Mantenimiento preventivo").
4. Haga clic en **"Guardar Movimiento"**.

> [!IMPORTANT]
> El sistema valida automáticamente si hay stock suficiente para Salidas y Transferencias. Si no hay suficiente, el sistema mostrará un error y no permitirá guardar el movimiento.

---

## 5. Consulta de Stock

En la sección **"Stock"** podrá visualizar las existencias actuales:
- Use las **pestañas superiores** para filtrar por tipo (Químicos, Tuberías, etc.).
- Use la **barra de búsqueda** para encontrar un artículo por nombre, código o marca.
- **Estados de Stock**:
  - 🟢 **Normal**: Stock suficiente.
  - 🟡 **Bajo**: Stock cerca o en el mínimo de seguridad.
  - 🔴 **Sin stock**: Existencia cero.

---

## 6. Reportes y Alertas

### Alertas de Stock Bajo
La sección **"Alertas"** muestra una lista consolidada de todos los artículos que requieren reposición inmediata. Es vital revisar esta sección diariamente.

### Reportes
En **"Reportes"** (solo Admin), puede generar visualizaciones y resúmenes de:
- Consumo por acueducto.
- Historial de movimientos detallado.
- Valorización del inventario.

---

## 7. Administración (Solo Administradores)

### Usuarios
Gestión de cuentas de acceso, asignación de roles y sucursales.

### Configuración del Sistema
Gestión de las entidades base:
- **Sucursales y Acueductos**: Definición de la estructura física.
- **Categorías**: Clasificación de productos.
- **Unidades de Medida**: (kg, metros, unidades, galones).
- **Proveedores**: Directorio de suministradores.

---

## 🆘 Soporte y Problemas Comunes

- **"No puedo ver el botón de Nuevo Artículo"**: Probablemente su rol es OPERADOR. Contacte a un administrador para cambios en el catálogo.
- **"Error al guardar movimiento: Stock insuficiente"**: Verifique la cantidad disponible en la sección de Stock antes de realizar la salida.
- **"El servidor no responde"**: Verifique su conexión de red o contacte al departamento de TI.
