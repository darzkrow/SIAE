# Documentación Swagger/OpenAPI - GSIH Inventario

**Fecha**: 8 de Enero de 2026  
**Status**: ✅ IMPLEMENTADO

---

## 📋 Instalación de drf-spectacular

Para implementar Swagger/OpenAPI en Django REST Framework, instala:

```bash
pip install drf-spectacular
```

---

## 🔧 Configuración en settings.py

Agrega lo siguiente a `config/settings.py`:

```python
INSTALLED_APPS = [
    # ... otras apps
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'GSIH Inventario API',
    'DESCRIPTION': 'API REST para Sistema de Gestión de Inventario Hidroeléctrico',
    'VERSION': '1.0.0',
    'SERVE_PERMISSIONS': ['rest_framework.permissions.IsAuthenticated'],
    'SERVERS': [
        {'url': 'http://localhost:8000', 'description': 'Desarrollo'},
        {'url': 'https://api.gsih.com', 'description': 'Producción'},
    ],
    'CONTACT': {
        'name': 'GSIH Support',
        'email': 'support@gsih.com',
    },
    'LICENSE': {
        'name': 'MIT',
    },
}
```

---

## 🔗 Configuración de URLs

Agrega lo siguiente a `config/urls.py`:

```python
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # ... otras URLs
    
    # Swagger/OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
```

---

## 📚 Endpoints Documentados

### Autenticación

#### Login
```
POST /api/accounts/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}

Response: 200 OK
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Perfil de Usuario
```
GET /api/accounts/me/
Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": 1,
  "username": "admin",
  "email": "admin@gsih.com",
  "role": "ADMIN",
  "sucursal": 1,
  "sucursal_nombre": "Planta A"
}
```

### Gestión de Inventario

#### Listar Tuberías
```
GET /api/tuberias/?search=pvc&material=PVC&limit=10
Authorization: Bearer <access_token>

Response: 200 OK
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "nombre": "Tubería PVC 2 pulgadas",
      "material": "PVC",
      "diametro": 2.0,
      "descripcion": "Tubería de PVC para sistemas de agua",
      "categoria": 1,
      "categoria_nombre": "Tuberías"
    }
  ]
}
```

#### Crear Tubería
```
POST /api/tuberias/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "nombre": "Tubería PVC 3 pulgadas",
  "material": "PVC",
  "diametro": 3.0,
  "descripcion": "Nueva tubería",
  "categoria": 1
}

Response: 201 Created
{
  "id": 2,
  "nombre": "Tubería PVC 3 pulgadas",
  ...
}
```

### Movimientos de Inventario

#### Crear Movimiento
```
POST /api/movimientos/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "tipo_movimiento": "ENTRADA",
  "tuberia": 1,
  "cantidad": 50,
  "acueducto_destino": 1,
  "razon": "Compra a proveedor"
}

Response: 201 Created
{
  "id": 1,
  "tipo_movimiento": "ENTRADA",
  "articulo_nombre": "Tubería PVC 2 pulgadas",
  "cantidad": 50,
  "fecha_movimiento": "2026-01-08T10:30:00Z",
  "usuario": "admin"
}
```

#### Listar Movimientos
```
GET /api/movimientos/?tipo_movimiento=ENTRADA&limit=20
Authorization: Bearer <access_token>

Response: 200 OK
{
  "count": 10,
  "results": [...]
}
```

### Reportes y Búsqueda

#### Dashboard Stats
```
GET /api/reportes/dashboard_stats/
Authorization: Bearer <access_token>

Response: 200 OK
{
  "total_tuberias": 5,
  "total_equipos": 3,
  "total_sucursales": 2,
  "total_acueductos": 4,
  "total_stock_tuberias": 150,
  "total_stock_equipos": 25,
  "alertas_activas": 2,
  "movimientos_hoy": 5
}
```

#### Búsqueda de Stock
```
GET /api/reportes/stock_search/?articulo_id=1&tipo=tuberia
Authorization: Bearer <access_token>

Response: 200 OK
{
  "articulo_id": 1,
  "articulo": "Tubería PVC 2 pulgadas",
  "tipo": "tuberia",
  "total_ubicaciones": 3,
  "stock_total": 150,
  "resultados": [
    {
      "id": 10,
      "acueducto": "Sistema Principal",
      "sucursal": "Planta A",
      "cantidad": 50,
      "estado": "normal"
    }
  ]
}
```

#### Búsqueda Avanzada
```
GET /api/reportes/stock_search_advanced/?nombre=motor&stock_bajo=true&tipo=equipo
Authorization: Bearer <access_token>

Response: 200 OK
{
  "filtros": {
    "nombre": "motor",
    "stock_bajo": true,
    "tipo": "equipo"
  },
  "total_resultados": 2,
  "stock_total": 8,
  "resultados": [...]
}
```

---

## 🔐 Autenticación en Swagger

1. Accede a `http://localhost:8000/api/docs/`
2. Haz clic en "Authorize"
3. Ingresa el token JWT en el formato: `Bearer <token>`
4. Haz clic en "Authorize"

---

## 📊 Esquemas de Datos

### Tubería
```json
{
  "id": 1,
  "nombre": "Tubería PVC 2 pulgadas",
  "material": "PVC",
  "diametro": 2.0,
  "tipo_uso": "Agua",
  "descripcion": "Descripción",
  "categoria": 1,
  "categoria_nombre": "Tuberías"
}
```

### Equipo
```json
{
  "id": 1,
  "nombre": "Motor de Bombeo 5HP",
  "marca": "Siemens",
  "modelo": "IE3",
  "numero_serie": "SN123456",
  "descripcion": "Descripción",
  "categoria": 1,
  "categoria_nombre": "Motores"
}
```

### Movimiento
```json
{
  "id": 1,
  "tipo_movimiento": "ENTRADA",
  "tuberia": 1,
  "equipo": null,
  "cantidad": 50,
  "acueducto_origen": null,
  "acueducto_destino": 1,
  "razon": "Compra",
  "fecha_movimiento": "2026-01-08T10:30:00Z",
  "usuario": "admin",
  "articulo_nombre": "Tubería PVC 2 pulgadas"
}
```

---

## 🧪 Pruebas en Swagger

1. Accede a `http://localhost:8000/api/docs/`
2. Selecciona un endpoint
3. Haz clic en "Try it out"
4. Completa los parámetros
5. Haz clic en "Execute"

---

## 📖 Documentación Alternativa

### ReDoc
- URL: `http://localhost:8000/api/redoc/`
- Interfaz alternativa más limpia
- Mejor para lectura de documentación

### Schema JSON
- URL: `http://localhost:8000/api/schema/`
- Esquema OpenAPI en formato JSON
- Útil para herramientas externas

---

## 🔧 Personalización de Documentación

### Agregar Descripción a Endpoints

```python
from drf_spectacular.utils import extend_schema

class TuberiaViewSet(viewsets.ModelViewSet):
    @extend_schema(
        description="Listar todas las tuberías disponibles",
        parameters=[
            OpenApiParameter('search', str, description='Buscar por nombre'),
            OpenApiParameter('material', str, description='Filtrar por material'),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
```

### Agregar Ejemplos

```python
from drf_spectacular.utils import extend_schema_field

class TuberiaSerializer(serializers.ModelSerializer):
    @extend_schema_field(serializers.CharField(example="Tubería PVC 2 pulgadas"))
    def get_nombre(self, obj):
        return obj.nombre
```

---

## 📝 Notas

- La documentación se genera automáticamente desde el código
- Usa docstrings en modelos y viewsets
- Personaliza con decoradores de drf-spectacular
- Mantén la documentación actualizada

---

**Status**: ✅ LISTO PARA IMPLEMENTAR
