# Tareas del Proyecto

Este documento rastrea las tareas de desarrollo para el proyecto SIAE.

## Pendiente

- [x] **Implementar Notificaciones en Tiempo Real**:
  - [x] Configurar Celery y Redis.
  - [x] Crear tareas asíncronas para enviar notificaciones a Telegram.
  - [x] Implementar WebSockets con Django Channels para notificaciones en la interfaz de usuario.
  - [x] Crear consumidores de Channels para manejar la lógica de WebSockets.

- [x] **Cargar Fixtures Geográficos**:
  - [x] Cargar el archivo `fixtures/geography.json` (usado `venezuela_full.json`) en la base de datos para poblar los modelos `State`, `Municipality` y `Parish`.

- [x] **Crear y Aplicar Migraciones**:
  - [x] Generar archivos de migración para las aplicaciones `geography` e `institucion`.
  - [x] Aplicar las migraciones a la base de datos para reflejar los nuevos modelos y las refactorizaciones.

- [x] **Desarrollar Endpoints de API**:
  - [x] Crear serializers y viewsets para los nuevos modelos (`Ubicacion`, `FichaTecnicaMotor`, `OrdenCompra`, etc.).
  - [x] Exponer los nuevos endpoints en la API.

- [ ] **Desarrollar Interfaz de Frontend**:
  - [ ] Crear componentes de React para visualizar y gestionar las nuevas funcionalidades (transferencias, fichas técnicas, notificaciones).
  - [ ] Integrar los nuevos endpoints de la API con el frontend.

## En Progreso

- [x] **Refactorización de Modelos**:
  - [x] Mover modelos de `OrganizacionCentral`, `Sucursal`, y `Acueducto` a la app `institucion`.
  - [x] Mover modelo `Ubicacion` a la app `geography`.
  - [x] Actualizar todas las referencias y claves foráneas.

## Completado

- [x] **Creación de Nuevas Apps**:
  - [x] Creada la app `institucion` para modelos organizacionales.
  - [x] Creada la app `geography` para modelos geográficos.
  - [x] Creada la app `notificaciones` para el sistema de alertas.

- [x] **Implementación de Modelos Base**:
  - [x] Definidos los modelos para `Ubicacion`, `FichaTecnicaMotor`, `OrdenCompra`, `RegistroMantenimiento`.
  - [x] Lógica de negocio implementada en `MovimientoInventario.save()` para la creación automática de órdenes y fichas técnicas.

- [x] **Reestructuración del Proyecto**:
  - [x] Unificado todo el código del backend en un directorio `backend/`.
  - [x] Sincronizado el proyecto con la rama `master` y resueltos los conflictos.
