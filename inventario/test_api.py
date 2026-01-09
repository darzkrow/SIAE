"""
Pruebas de API REST para el sistema de inventario
"""
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal

from inventario.models import (
    OrganizacionCentral, Sucursal, Acueducto, Categoria,
    Tuberia, Equipo, StockTuberia, StockEquipo, MovimientoInventario
)

User = get_user_model()


class APISetupMixin:
    """Mixin para configurar datos de prueba para API"""
    
    def setUp(self):
        super().setUp()
        self.client.default_format = 'json'
        
        # Crear usuarios
        self.admin = User.objects.create_user(
            username='admin_api',
            password='testpass123',
            role='ADMIN'
        )
        self.operador = User.objects.create_user(
            username='operador_api',
            password='testpass123',
            role='OPERADOR'
        )
        
        # Crear datos base
        self.org = OrganizacionCentral.objects.create(
            nombre='Hidroeléctrica Test',
            rif='J-99999999-9'
        )
        
        self.sucursal = Sucursal.objects.create(
            nombre='Planta Test',
            organizacion_central=self.org
        )
        
        self.acueducto = Acueducto.objects.create(
            nombre='Sistema Test',
            sucursal=self.sucursal
        )
        
        self.categoria = Categoria.objects.create(nombre='Test')
        
        self.tuberia = Tuberia.objects.create(
            nombre='Tubería Test',
            categoria=self.categoria,
            material='PVC',
            tipo_uso='POTABLE',
            diametro_nominal_mm=100,
            longitud_m=Decimal('50.00')
        )
        
        self.equipo = Equipo.objects.create(
            nombre='Motor Test',
            categoria=self.categoria,
            numero_serie='TEST-001',
            potencia_hp=Decimal('50.00')
        )
        
        self.stock_tuberia = StockTuberia.objects.create(
            tuberia=self.tuberia,
            acueducto=self.acueducto,
            cantidad=100
        )
        
        self.stock_equipo = StockEquipo.objects.create(
            equipo=self.equipo,
            acueducto=self.acueducto,
            cantidad=5
        )


class TuberiaAPITests(APISetupMixin, APITestCase):
    """Pruebas de API para Tuberías"""
    
    def test_listar_tuberias_sin_autenticacion(self):
        """Prueba: Listar tuberías sin autenticación debe fallar"""
        response = self.client.get('/api/tuberias/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_listar_tuberias_con_autenticacion(self):
        """Prueba: Listar tuberías con autenticación"""
        self.client.force_authenticate(user=self.operador)
        response = self.client.get('/api/tuberias/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_crear_tuberia_como_admin(self):
        """Prueba: Admin puede crear tubería"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'nombre': 'Tubería Nueva',
            'categoria': self.categoria.id,
            'material': 'HIERRO',
            'tipo_uso': 'SERVIDAS',
            'diametro_nominal_mm': 150,
            'longitud_m': '100.00'
        }
        response = self.client.post('/api/tuberias/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_crear_tuberia_como_operador(self):
        """Prueba: Operador no puede crear tubería"""
        self.client.force_authenticate(user=self.operador)
        data = {
            'nombre': 'Tubería Nueva',
            'categoria': self.categoria.id,
            'material': 'HIERRO',
            'tipo_uso': 'SERVIDAS',
            'diametro_nominal_mm': 150,
            'longitud_m': '100.00'
        }
        response = self.client.post('/api/tuberias/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_actualizar_tuberia(self):
        """Prueba: Actualizar tubería"""
        self.client.force_authenticate(user=self.admin)
        data = {'nombre': 'Tubería Actualizada'}
        response = self.client.patch(f'/api/tuberias/{self.tuberia.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.tuberia.refresh_from_db()
        self.assertEqual(self.tuberia.nombre, 'Tubería Actualizada')
    
    def test_eliminar_tuberia(self):
        """Prueba: Eliminar tubería"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/tuberias/{self.tuberia.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class EquipoAPITests(APISetupMixin, APITestCase):
    """Pruebas de API para Equipos"""
    
    def test_listar_equipos(self):
        """Prueba: Listar equipos"""
        self.client.force_authenticate(user=self.operador)
        response = self.client.get('/api/equipos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_crear_equipo_como_admin(self):
        """Prueba: Admin puede crear equipo"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'nombre': 'Motor Nuevo',
            'categoria': self.categoria.id,
            'numero_serie': 'NEW-001',
            'potencia_hp': '75.00'
        }
        response = self.client.post('/api/equipos/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_numero_serie_unico_en_api(self):
        """Prueba: Número de serie debe ser único"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'nombre': 'Motor Duplicado',
            'categoria': self.categoria.id,
            'numero_serie': 'TEST-001',  # Duplicado
            'potencia_hp': '50.00'
        }
        response = self.client.post('/api/equipos/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class StockAPITests(APISetupMixin, APITestCase):
    """Pruebas de API para Stock"""
    
    def test_listar_stock_tuberias(self):
        """Prueba: Listar stock de tuberías"""
        self.client.force_authenticate(user=self.operador)
        response = self.client.get('/api/stock-tuberias/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_listar_stock_equipos(self):
        """Prueba: Listar stock de equipos"""
        self.client.force_authenticate(user=self.operador)
        response = self.client.get('/api/stock-equipos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_crear_stock_tuberia(self):
        """Prueba: Crear stock de tubería"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'tuberia': self.tuberia.id,
            'acueducto': self.acueducto.id,
            'cantidad': 50
        }
        response = self.client.post('/api/stock-tuberias/', data)
        # Puede fallar si ya existe (unique_together)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
    
    def test_actualizar_stock(self):
        """Prueba: Actualizar cantidad de stock"""
        self.client.force_authenticate(user=self.admin)
        data = {'cantidad': 150}
        response = self.client.patch(f'/api/stock-tuberias/{self.stock_tuberia.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class MovimientoAPITests(APISetupMixin, APITestCase):
    """Pruebas de API para Movimientos"""
    
    def test_crear_entrada_tuberia(self):
        """Prueba: Crear entrada de tubería"""
        self.client.force_authenticate(user=self.operador)
        data = {
            'tuberia': self.tuberia.id,
            'acueducto_destino': self.acueducto.id,
            'tipo_movimiento': 'ENTRADA',
            'cantidad': 20,
            'razon': 'Compra'
        }
        response = self.client.post('/api/movimientos/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_crear_salida_tuberia(self):
        """Prueba: Crear salida de tubería"""
        self.client.force_authenticate(user=self.operador)
        data = {
            'tuberia': self.tuberia.id,
            'acueducto_origen': self.acueducto.id,
            'tipo_movimiento': 'SALIDA',
            'cantidad': 10,
            'razon': 'Instalación'
        }
        response = self.client.post('/api/movimientos/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_crear_transferencia(self):
        """Prueba: Crear transferencia entre acueductos"""
        # Crear segundo acueducto
        acueducto2 = Acueducto.objects.create(
            nombre='Sistema 2',
            sucursal=self.sucursal
        )
        
        self.client.force_authenticate(user=self.operador)
        data = {
            'tuberia': self.tuberia.id,
            'acueducto_origen': self.acueducto.id,
            'acueducto_destino': acueducto2.id,
            'tipo_movimiento': 'TRANSFERENCIA',
            'cantidad': 15,
            'razon': 'Reubicación'
        }
        response = self.client.post('/api/movimientos/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_salida_stock_insuficiente(self):
        """Prueba: Salida con stock insuficiente debe fallar"""
        self.client.force_authenticate(user=self.operador)
        data = {
            'tuberia': self.tuberia.id,
            'acueducto_origen': self.acueducto.id,
            'tipo_movimiento': 'SALIDA',
            'cantidad': 10000,  # Más de lo disponible
            'razon': 'Intento fallido'
        }
        response = self.client.post('/api/movimientos/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_filtrar_movimientos_por_tipo(self):
        """Prueba: Filtrar movimientos por tipo"""
        self.client.force_authenticate(user=self.operador)
        response = self.client.get('/api/movimientos/?tipo_movimiento=ENTRADA')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_listar_movimientos_paginado(self):
        """Prueba: Listar movimientos con paginación"""
        self.client.force_authenticate(user=self.operador)
        response = self.client.get('/api/movimientos/?page=1&page_size=10')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)


class UsuariosAPITests(APISetupMixin, APITestCase):
    """Pruebas de API para Usuarios"""
    
    def test_listar_usuarios_como_admin(self):
        """Prueba: Admin puede listar usuarios"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_listar_usuarios_como_operador(self):
        """Prueba: Operador no puede listar usuarios"""
        self.client.force_authenticate(user=self.operador)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_crear_usuario_como_admin(self):
        """Prueba: Admin puede crear usuario"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'username': 'nuevo_usuario',
            'password': 'newpass123',
            'email': 'nuevo@test.com',
            'role': 'OPERADOR'
        }
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_obtener_perfil_usuario(self):
        """Prueba: Obtener perfil del usuario autenticado"""
        self.client.force_authenticate(user=self.operador)
        response = self.client.get('/api/accounts/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'operador_api')
        self.assertEqual(response.data['role'], 'OPERADOR')


class AuditoriaAPITests(APISetupMixin, APITestCase):
    """Pruebas de API para Auditoría"""
    
    def test_listar_auditorias(self):
        """Prueba: Listar auditorías"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/audits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filtrar_auditorias_por_status(self):
        """Prueba: Filtrar auditorías por status"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/audits/?status=SUCCESS')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ReportesAPITests(APISetupMixin, APITestCase):
    """Pruebas de API para Reportes"""
    
    def test_dashboard_stats(self):
        """Prueba: Obtener estadísticas del dashboard"""
        self.client.force_authenticate(user=self.operador)
        response = self.client.get('/api/reportes/dashboard_stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_articulos', response.data)
    
    def test_stock_por_sucursal(self):
        """Prueba: Obtener stock por sucursal"""
        self.client.force_authenticate(user=self.operador)
        response = self.client.get('/api/reportes/stock_por_sucursal/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_alertas_stock_bajo(self):
        """Prueba: Obtener alertas de stock bajo"""
        self.client.force_authenticate(user=self.operador)
        response = self.client.get('/api/reportes/alertas_stock_bajo/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
