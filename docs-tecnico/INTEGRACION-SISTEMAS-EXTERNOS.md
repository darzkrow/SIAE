# Integración con Sistemas Externos - Fase 4

**Fecha**: 8 de Enero de 2026  
**Status**: 📋 DISEÑO Y ESPECIFICACIÓN

---

## 🎯 Objetivo

Permitir que GSIH Inventario se integre con sistemas externos como ERP, sistemas de compras y otros sistemas de gestión.

---

## 🔌 Tipos de Integración

### 1. API REST para Sistemas Externos

#### Endpoints Disponibles

```
GET    /api/external/articulos/
POST   /api/external/articulos/
GET    /api/external/stock/
POST   /api/external/movimientos/
GET    /api/external/reportes/
```

#### Autenticación

```python
# Usar API Keys en lugar de JWT para sistemas externos

class ExternalAPIKey(models.Model):
    nombre = models.CharField(max_length=100)
    clave = models.CharField(max_length=255, unique=True)
    sistema = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.sistema}"
```

#### Middleware de Autenticación

```python
class ExternalAPIAuthentication(authentication.TokenAuthentication):
    keyword = 'ApiKey'
    model = ExternalAPIKey
    
    def get_model(self):
        return ExternalAPIKey
```

### 2. Webhooks para Notificaciones

#### Modelo de Webhook

```python
class Webhook(models.Model):
    EVENTO_CHOICES = [
        ('movimiento_creado', 'Movimiento Creado'),
        ('stock_bajo', 'Stock Bajo'),
        ('alerta_generada', 'Alerta Generada'),
        ('movimiento_aprobado', 'Movimiento Aprobado'),
    ]
    
    nombre = models.CharField(max_length=100)
    url = models.URLField()
    evento = models.CharField(max_length=50, choices=EVENTO_CHOICES)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.evento}"
```

#### Envío de Webhook

```python
import requests
from celery import shared_task

@shared_task
def enviar_webhook(webhook_id, evento_data):
    webhook = Webhook.objects.get(id=webhook_id)
    
    try:
        response = requests.post(
            webhook.url,
            json=evento_data,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
    except requests.RequestException as e:
        # Reintentar después
        enviar_webhook.retry(exc=e, countdown=60)
```

### 3. Sincronización con ERP

#### Modelo de Sincronización

```python
class SincronizacionERP(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('SINCRONIZADO', 'Sincronizado'),
        ('ERROR', 'Error'),
    ]
    
    tipo = models.CharField(max_length=50)  # articulo, stock, movimiento
    referencia_externa = models.CharField(max_length=255)
    referencia_interna = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    datos = models.JSONField()
    error = models.TextField(blank=True)
    fecha_sincronizacion = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('tipo', 'referencia_externa')
```

#### Sincronización Bidireccional

```python
class SincronizadorERP:
    def __init__(self, url_erp, api_key):
        self.url_erp = url_erp
        self.api_key = api_key
    
    def sincronizar_articulos(self):
        """Sincronizar artículos desde ERP"""
        response = requests.get(
            f"{self.url_erp}/api/articulos",
            headers={'Authorization': f'Bearer {self.api_key}'}
        )
        
        for articulo_data in response.json():
            self._crear_o_actualizar_articulo(articulo_data)
    
    def sincronizar_stock(self):
        """Sincronizar stock desde ERP"""
        # Implementación similar
        pass
    
    def enviar_movimiento(self, movimiento):
        """Enviar movimiento al ERP"""
        data = {
            'tipo': movimiento.tipo_movimiento,
            'articulo': movimiento.articulo_id,
            'cantidad': movimiento.cantidad,
            'fecha': movimiento.fecha_movimiento.isoformat()
        }
        
        response = requests.post(
            f"{self.url_erp}/api/movimientos",
            json=data,
            headers={'Authorization': f'Bearer {self.api_key}'}
        )
        
        return response.json()
```

### 4. Importación de Datos

#### Importador CSV

```python
import csv
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('archivo', type=str)
        parser.add_argument('--tipo', type=str, choices=['articulos', 'stock'])
    
    def handle(self, *args, **options):
        archivo = options['archivo']
        tipo = options['tipo']
        
        with open(archivo, 'r') as f:
            reader = csv.DictReader(f)
            
            if tipo == 'articulos':
                self._importar_articulos(reader)
            elif tipo == 'stock':
                self._importar_stock(reader)
    
    def _importar_articulos(self, reader):
        for row in reader:
            Tuberia.objects.create(
                nombre=row['nombre'],
                material=row['material'],
                diametro=float(row['diametro'])
            )
```

---

## 📊 Ejemplos de Integración

### Ejemplo 1: Sincronización con ERP SAP

```python
# Configuración
ERP_CONFIG = {
    'url': 'https://sap.empresa.com/api',
    'api_key': 'your-api-key',
    'sincronizar_cada': 3600  # cada hora
}

# Usar
sincronizador = SincronizadorERP(ERP_CONFIG['url'], ERP_CONFIG['api_key'])
sincronizador.sincronizar_articulos()
sincronizador.sincronizar_stock()
```

### Ejemplo 2: Webhook para Sistema de Compras

```python
# Crear webhook
webhook = Webhook.objects.create(
    nombre='Sistema de Compras',
    url='https://compras.empresa.com/webhook',
    evento='stock_bajo',
    activo=True
)

# Cuando se genera alerta de stock bajo
alerta = AlertaStock.objects.create(...)
enviar_webhook.delay(webhook.id, {
    'evento': 'stock_bajo',
    'articulo': alerta.articulo.nombre,
    'cantidad_actual': alerta.cantidad_actual,
    'umbral_minimo': alerta.umbral_minimo
})
```

### Ejemplo 3: API Key para Sistema Externo

```python
# Crear API Key
api_key = ExternalAPIKey.objects.create(
    nombre='Sistema de Reportes',
    clave='sk_live_abc123def456',
    sistema='Reportes',
    fecha_expiracion=timezone.now() + timedelta(days=365)
)

# Usar en cliente externo
curl -H "Authorization: ApiKey sk_live_abc123def456" \
     https://gsih.com/api/external/stock/
```

---

## 🔐 Seguridad

### Validación de Webhooks

```python
import hmac
import hashlib

def validar_webhook(payload, signature, secret):
    """Validar firma de webhook"""
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
```

### Rate Limiting para APIs Externas

```python
from rest_framework.throttling import UserRateThrottle

class ExternalAPIThrottle(UserRateThrottle):
    scope = 'external_api'
    THROTTLE_RATES = {
        'external_api': '1000/hour'
    }
```

---

## 📈 Monitoreo

### Log de Integraciones

```python
class LogIntegracion(models.Model):
    sistema = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    estado = models.CharField(max_length=20)
    datos_enviados = models.JSONField()
    datos_recibidos = models.JSONField(null=True)
    error = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha']
```

### Dashboard de Integraciones

```
GET /api/reportes/integraciones/

Response:
{
  "total_sincronizaciones": 1000,
  "exitosas": 980,
  "fallidas": 20,
  "tasa_exito": 98.0,
  "ultima_sincronizacion": "2026-01-08T10:30:00Z",
  "proxima_sincronizacion": "2026-01-08T11:30:00Z"
}
```

---

## 🧪 Pruebas

### Test de Webhook

```python
def test_webhook_stock_bajo():
    webhook = Webhook.objects.create(
        nombre='Test',
        url='https://example.com/webhook',
        evento='stock_bajo'
    )
    
    alerta = AlertaStock.objects.create(...)
    
    # Simular envío
    with patch('requests.post') as mock_post:
        enviar_webhook(webhook.id, {'evento': 'stock_bajo'})
        mock_post.assert_called_once()
```

---

## 📋 Checklist de Implementación

- [ ] Crear modelo de API Key
- [ ] Implementar autenticación externa
- [ ] Crear endpoints para sistemas externos
- [ ] Implementar webhooks
- [ ] Crear sincronizador ERP
- [ ] Implementar importador CSV
- [ ] Agregar validación de webhooks
- [ ] Implementar rate limiting
- [ ] Crear log de integraciones
- [ ] Agregar dashboard de monitoreo
- [ ] Pruebas completas
- [ ] Documentación de API

---

**Status**: 📋 ESPECIFICACIÓN COMPLETA - LISTO PARA IMPLEMENTAR
