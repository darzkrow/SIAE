"""
Pruebas unitarias completas para el sistema de inventario de hidroeléctrica.
Incluye pruebas de modelos, serializers, views y lógica de movimientos.
"""
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal

from inventario.models import (
    OrganizacionCentral, Sucursal, Acueducto, Categoria,
    Tuberia, Equipo, StockTuberia, StockEquipo,
    MovimientoInventario, AlertaStock, InventoryAudit
)
from inventario.serializers import (
    TuberiaSerializer, EquipoSerializer, StockTuberiaSerializer,
    StockEquipoSerializer, MovimientoInventarioSerializer
)

User = get_user_model()


class SetupTestDataMixin:
    """Mixin para crear datos de prueba realistas para una hidroeléctrica"""
    
    def setUp(self):
        super().setUp()
        
        # Crear organización central
        self.org = OrganizacionCentral.objects.create(
            nombre='Hidroeléctrica Central',
            rif='J-12345678-9'
        )
        
        # Crear sucursales (plantas hidroeléctricas)
        self.sucursal_principal = Sucursal.objects.create(
            nombre='Planta Principal - Caroní',
            organizacion_central=self.org
        )
        self.sucursal_secundaria = Sucursal.objects.create(
            nombre='Planta Secundaria - Orinoco',
            organizacion_central=self.org
        )
        
        # Crear acueductos (sistemas de distribución dentro de cada planta)
        self.acueducto_principal = Acueducto.objects.create(
            nombre='Sistema de Bombeo Principal',
            sucursal=self.sucursal_principal
        )
        self.acueducto_secundario = Acueducto.objects.create(
            nombre='Sistema de Distribución Secundario',
            sucursal=self.sucursal_principal
        )
        self.acueducto_otra_sucursal = Acueducto.objects.create(
            nombre='Sistema de Bombeo Orinoco',
            sucursal=self.sucursal_secundaria
        )
        
        # Crear categorías
        self.cat_tuberias = Categoria.objects.create(nombre='Tuberías')
        self.cat_motores = Categoria.objects.create(nombre='Motores de Bombeo')
        self.cat_bombas = Categoria.objects.create(nombre='Bombas Centrífugas')
        self.cat_valvulas = Categoria.objects.create(nombre='Válvulas')
        
        # Crear tuberías (artículos operativos)
        self.tuberia_pvc_100 = Tuberia.objects.create(
            nombre='Tubería PVC 100mm - Agua Potable',
            descripcion='Tubería de PVC para sistemas de agua potable',
            categoria=self.cat_tuberias,
            material=Tuberia.MATERIAL_PVC,
            tipo_uso=Tuberia.USO_POTABLE,
            diametro_nominal_mm=100,
            longitud_m=Decimal('50.00')
        )
        self.tuberia_hierro_150 = Tuberia.objects.create(
            nombre='Tubería Hierro Dúctil 150mm - Aguas Servidas',
            descripcion='Tubería de hierro dúctil para aguas servidas',
            categoria=self.cat_tuberias,
            material=Tuberia.MATERIAL_HIERRO,
            tipo_uso=Tuberia.USO_SERVIDAS,
            diametro_nominal_mm=150,
            longitud_m=Decimal('100.00')
        )
        self.tuberia_cemento_200 = Tuberia.objects.create(
            nombre='Tubería Cemento 200mm - Riego',
            descripcion='Tubería de cemento para sistemas de riego',
            categoria=self.cat_tuberias,
            material=Tuberia.MATERIAL_CEMENTO,
            tipo_uso=Tuberia.USO_RIEGO,
            diametro_nominal_mm=200,
            longitud_m=Decimal('75.00')
        )
        
        # Crear equipos (motores de bombeo y otros equipos operativos)
        self.motor_bombeo_50hp = Equipo.objects.create(
            nombre='Motor de Bombeo Centrífugo 50 HP',
            descripcion='Motor trifásico para bombeo de agua',
            categoria=self.cat_motores,
            marca='Siemens',
            modelo='IE3-100L-4',
            potencia_hp=Decimal('50.00'),
            numero_serie='SIE-2024-001'
        )
        self.motor_bombeo_75hp = Equipo.objects.create(
            nombre='Motor de Bombeo Centrífugo 75 HP',
            descripcion='Motor trifásico de alta potencia',
            categoria=self.cat_motores,
            marca='ABB',
            modelo='M3BP-225M-4',
            potencia_hp=Decimal('75.00'),
            numero_serie='ABB-2024-001'
        )
        self.bomba_centrifuga = Equipo.objects.create(
            nombre='Bomba Centrífuga 100m³/h',
            descripcion='Bomba para sistemas de distribución',
            categoria=self.cat_bombas,
            marca='Grundfos',
            modelo='CR-100-2-2',
            potencia_hp=Decimal('30.00'),
            numero_serie='GRU-2024-001'
        )
        self.valvula_compuerta = Equipo.objects.create(
            nombre='Válvula de Compuerta 150mm',
            descripcion='Válvula de control de flujo',
            categoria=self.cat_valvulas,
            marca='Watts',
            modelo='WC-150',
            numero_serie='WAT-2024-001'
        )
        
        # Crear stock inicial
        self.stock_tuberia_pvc = StockTuberia.objects.create(
            tuberia=self.tuberia_pvc_100,
            acueducto=self.acueducto_principal,
            cantidad=50
        )
        self.stock_tuberia_hierro = StockTuberia.objects.create(
            tuberia=self.tuberia_hierro_150,
            acueducto=self.acueducto_principal,
            cantidad=30
        )
        self.stock_motor_50hp = StockEquipo.objects.create(
            equipo=self.motor_bombeo_50hp,
            acueducto=self.acueducto_principal,
            cantidad=3
        )
        self.stock_motor_75hp = StockEquipo.objects.create(
            equipo=self.motor_bombeo_75hp,
            acueducto=self.acueducto_principal,
            cantidad=2
        )
        self.stock_bomba = StockEquipo.objects.create(
            equipo=self.bomba_centrifuga,
            acueducto=self.acueducto_principal,
            cantidad=5
        )
        
        # Crear usuarios de prueba
        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='testpass123',
            email='admin@test.com',
            role='ADMIN'
        )
        self.operador_user = User.objects.create_user(
            username='operador_test',
            password='testpass123',
            email='operador@test.com',
            role='OPERADOR'
        )


class TuberiaModelTests(SetupTestDataMixin, TestCase):
    """Pruebas del modelo Tubería"""
    
    def test_crear_tuberia_pvc(self):
        """Verificar creación de tubería PVC"""
        self.assertEqual(self.tuberia_pvc_100.material, Tuberia.MATERIAL_PVC)
        self.assertEqual(self.tuberia_pvc_100.tipo_uso, Tuberia.USO_POTABLE)
        self.assertEqual(self.tuberia_pvc_100.diametro_nominal_mm, 100)
    
    def test_crear_tuberia_hierro(self):
        """Verificar creación de tubería de hierro dúctil"""
        self.assertEqual(self.tuberia_hierro_150.material, Tuberia.MATERIAL_HIERRO)
        self.assertEqual(self.tuberia_hierro_150.tipo_uso, Tuberia.USO_SERVIDAS)
    
    def test_tuberia_str(self):
        """Verificar representación en string"""
        self.assertIn('PVC', str(self.tuberia_pvc_100))
        self.assertIn('100mm', str(self.tuberia_pvc_100))


class EquipoModelTests(SetupTestDataMixin, TestCase):
    """Pruebas del modelo Equipo"""
    
    def test_crear_motor_bombeo(self):
        """Verificar creación de motor de bombeo"""
        self.assertEqual(self.motor_bombeo_50hp.potencia_hp, Decimal('50.00'))
        self.assertEqual(self.motor_bombeo_50hp.marca, 'Siemens')
    
    def test_numero_serie_unico(self):
        """Verificar que número de serie es único"""
        with self.assertRaises(Exception):
            Equipo.objects.create(
                nombre='Duplicado',
                categoria=self.cat_motores,
                numero_serie='SIE-2024-001'  # Duplicado
            )
    
    def test_equipo_str(self):
        """Verificar representación en string"""
        self.assertIn('50 HP', str(self.motor_bombeo_50hp))


class StockTuberiaModelTests(SetupTestDataMixin, TestCase):
    """Pruebas del modelo Stock de Tuberías"""
    
    def test_crear_stock_tuberia(self):
        """Verificar creación de stock"""
        self.assertEqual(self.stock_tuberia_pvc.cantidad, 50)
        self.assertEqual(self.stock_tuberia_pvc.tuberia, self.tuberia_pvc_100)
    
    def test_stock_cantidad_negativa_invalida(self):
        """Verificar que cantidad negativa es inválida"""
        stock = StockTuberia(
            tuberia=self.tuberia_pvc_100,
            acueducto=self.acueducto_principal,
            cantidad=-10
        )
        with self.assertRaises(ValidationError):
            stock.save()
    
    def test_unique_together_tuberia_acueducto(self):
        """Verificar restricción unique_together"""
        with self.assertRaises(Exception):
            StockTuberia.objects.create(
                tuberia=self.tuberia_pvc_100,
                acueducto=self.acueducto_principal,
                cantidad=100
            )


class MovimientoInventarioTests(SetupTestDataMixin, TransactionTestCase):
    """Pruebas de movimientos de inventario con lógica de transferencia"""
    
    def test_entrada_tuberia(self):
        """Prueba: Entrada de tuberías"""
        cantidad_inicial = self.stock_tuberia_pvc.cantidad
        
        movimiento = MovimientoInventario.objects.create(
            tuberia=self.tuberia_pvc_100,
            acueducto_destino=self.acueducto_principal,
            tipo_movimiento=MovimientoInventario.T_ENTRADA,
            cantidad=20,
            razon='Compra de tuberías nuevas'
        )
        
        self.stock_tuberia_pvc.refresh_from_db()
        self.assertEqual(self.stock_tuberia_pvc.cantidad, cantidad_inicial + 20)
    
    def test_salida_tuberia(self):
        """Prueba: Salida de tuberías"""
        cantidad_inicial = self.stock_tuberia_pvc.cantidad
        
        movimiento = MovimientoInventario.objects.create(
            tuberia=self.tuberia_pvc_100,
            acueducto_origen=self.acueducto_principal,
            tipo_movimiento=MovimientoInventario.T_SALIDA,
            cantidad=10,
            razon='Instalación en campo'
        )
        
        self.stock_tuberia_pvc.refresh_from_db()
        self.assertEqual(self.stock_tuberia_pvc.cantidad, cantidad_inicial - 10)
    
    def test_salida_stock_insuficiente(self):
        """Prueba: Salida con stock insuficiente debe fallar"""
        with self.assertRaises(ValidationError):
            MovimientoInventario.objects.create(
                tuberia=self.tuberia_pvc_100,
                acueducto_origen=self.acueducto_principal,
                tipo_movimiento=MovimientoInventario.T_SALIDA,
                cantidad=1000,  # Más de lo disponible
                razon='Intento de salida excesiva'
            )
    
    def test_transferencia_entre_sucursales(self):
        """Prueba: Transferencia entre sucursales (disminuye origen, aumenta destino)"""
        # Crear stock en sucursal secundaria
        stock_secundaria = StockTuberia.objects.create(
            tuberia=self.tuberia_pvc_100,
            acueducto=self.acueducto_otra_sucursal,
            cantidad=0
        )
        
        cantidad_inicial_principal = self.stock_tuberia_pvc.cantidad
        
        movimiento = MovimientoInventario.objects.create(
            tuberia=self.tuberia_pvc_100,
            acueducto_origen=self.acueducto_principal,
            acueducto_destino=self.acueducto_otra_sucursal,
            tipo_movimiento=MovimientoInventario.T_TRANSFER,
            cantidad=15,
            razon='Transferencia entre plantas'
        )
        
        self.stock_tuberia_pvc.refresh_from_db()
        stock_secundaria.refresh_from_db()
        
        # Verificar que disminuyó en origen y aumentó en destino
        self.assertEqual(self.stock_tuberia_pvc.cantidad, cantidad_inicial_principal - 15)
        self.assertEqual(stock_secundaria.cantidad, 15)
    
    def test_transferencia_mismo_acueducto_diferente_sucursal(self):
        """Prueba: Transferencia dentro de misma sucursal (solo cambio de ubicación)"""
        # Crear stock en acueducto secundario
        stock_secundario = StockTuberia.objects.create(
            tuberia=self.tuberia_pvc_100,
            acueducto=self.acueducto_secundario,
            cantidad=0
        )
        
        cantidad_inicial_principal = self.stock_tuberia_pvc.cantidad
        
        movimiento = MovimientoInventario.objects.create(
            tuberia=self.tuberia_pvc_100,
            acueducto_origen=self.acueducto_principal,
            acueducto_destino=self.acueducto_secundario,
            tipo_movimiento=MovimientoInventario.T_TRANSFER,
            cantidad=10,
            razon='Reubicación dentro de la planta'
        )
        
        self.stock_tuberia_pvc.refresh_from_db()
        stock_secundario.refresh_from_db()
        
        # Verificar que disminuyó en origen y aumentó en destino (cambio de ubicación)
        self.assertEqual(self.stock_tuberia_pvc.cantidad, cantidad_inicial_principal - 10)
        self.assertEqual(stock_secundario.cantidad, 10)
    
    def test_entrada_equipo(self):
        """Prueba: Entrada de equipos (motores de bombeo)"""
        cantidad_inicial = self.stock_motor_50hp.cantidad
        
        movimiento = MovimientoInventario.objects.create(
            equipo=self.motor_bombeo_50hp,
            acueducto_destino=self.acueducto_principal,
            tipo_movimiento=MovimientoInventario.T_ENTRADA,
            cantidad=2,
            razon='Compra de motores nuevos'
        )
        
        self.stock_motor_50hp.refresh_from_db()
        self.assertEqual(self.stock_motor_50hp.cantidad, cantidad_inicial + 2)
    
    def test_audit_movimiento_exitoso(self):
        """Prueba: Auditoría registra movimiento exitoso"""
        movimiento = MovimientoInventario.objects.create(
            tuberia=self.tuberia_pvc_100,
            acueducto_destino=self.acueducto_principal,
            tipo_movimiento=MovimientoInventario.T_ENTRADA,
            cantidad=5,
            razon='Prueba de auditoría'
        )
        
        audit = InventoryAudit.objects.get(movimiento=movimiento)
        self.assertEqual(audit.status, InventoryAudit.STATUS_SUCCESS)
        self.assertEqual(audit.cantidad, 5)
    
    def test_audit_movimiento_fallido(self):
        """Prueba: Auditoría registra movimiento fallido"""
        try:
            movimiento = MovimientoInventario.objects.create(
                tuberia=self.tuberia_pvc_100,
                acueducto_origen=self.acueducto_principal,
                tipo_movimiento=MovimientoInventario.T_SALIDA,
                cantidad=1000,
                razon='Intento fallido'
            )
        except ValidationError:
            pass
        
        audit = InventoryAudit.objects.filter(
            status=InventoryAudit.STATUS_FAILED
        ).first()
        self.assertIsNotNone(audit)


class AlertaStockTests(SetupTestDataMixin, TestCase):
    """Pruebas de alertas de stock bajo"""
    
    def test_crear_alerta_tuberia(self):
        """Prueba: Crear alerta para tubería"""
        alerta = AlertaStock.objects.create(
            tuberia=self.tuberia_pvc_100,
            acueducto=self.acueducto_principal,
            umbral_minimo=10,
            activo=True
        )
        
        self.assertEqual(alerta.umbral_minimo, 10)
        self.assertTrue(alerta.activo)
    
    def test_crear_alerta_equipo(self):
        """Prueba: Crear alerta para equipo"""
        alerta = AlertaStock.objects.create(
            equipo=self.motor_bombeo_50hp,
            acueducto=self.acueducto_principal,
            umbral_minimo=1,
            activo=True
        )
        
        self.assertEqual(alerta.umbral_minimo, 1)
    
    def test_alerta_no_permite_ambos_articulos(self):
        """Prueba: Alerta no puede tener tubería y equipo simultáneamente"""
        alerta = AlertaStock(
            tuberia=self.tuberia_pvc_100,
            equipo=self.motor_bombeo_50hp,
            acueducto=self.acueducto_principal,
            umbral_minimo=10
        )
        
        with self.assertRaises(ValidationError):
            alerta.clean()


class TuberiaSerializerTests(SetupTestDataMixin, TestCase):
    """Pruebas del serializador de Tuberías"""
    
    def test_serializar_tuberia(self):
        """Prueba: Serializar tubería"""
        serializer = TuberiaSerializer(self.tuberia_pvc_100)
        data = serializer.data
        
        self.assertEqual(data['nombre'], 'Tubería PVC 100mm - Agua Potable')
        self.assertEqual(data['material'], 'PVC')
        self.assertEqual(data['diametro_nominal_mm'], 100)
    
    def test_deserializar_tuberia(self):
        """Prueba: Deserializar y crear tubería"""
        data = {
            'nombre': 'Tubería PVC 75mm',
            'descripcion': 'Nueva tubería',
            'categoria': self.cat_tuberias.id,
            'material': 'PVC',
            'tipo_uso': 'POTABLE',
            'diametro_nominal_mm': 75,
            'longitud_m': '50.00'
        }
        
        serializer = TuberiaSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        tuberia = serializer.save()
        self.assertEqual(tuberia.diametro_nominal_mm, 75)


class EquipoSerializerTests(SetupTestDataMixin, TestCase):
    """Pruebas del serializador de Equipos"""
    
    def test_serializar_equipo(self):
        """Prueba: Serializar equipo"""
        serializer = EquipoSerializer(self.motor_bombeo_50hp)
        data = serializer.data
        
        self.assertEqual(data['nombre'], 'Motor de Bombeo Centrífugo 50 HP')
        self.assertEqual(data['marca'], 'Siemens')
        self.assertEqual(data['potencia_hp'], '50.00')
    
    def test_deserializar_equipo(self):
        """Prueba: Deserializar y crear equipo"""
        data = {
            'nombre': 'Motor de Bombeo 100 HP',
            'descripcion': 'Motor nuevo',
            'categoria': self.cat_motores.id,
            'marca': 'Siemens',
            'modelo': 'IE3-160L-4',
            'potencia_hp': '100.00',
            'numero_serie': 'SIE-2024-NEW'
        }
        
        serializer = EquipoSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        equipo = serializer.save()
        self.assertEqual(equipo.potencia_hp, Decimal('100.00'))


class StockSerializerTests(SetupTestDataMixin, TestCase):
    """Pruebas de serializadores de Stock"""
    
    def test_serializar_stock_tuberia(self):
        """Prueba: Serializar stock de tubería"""
        serializer = StockTuberiaSerializer(self.stock_tuberia_pvc)
        data = serializer.data
        
        self.assertEqual(data['cantidad'], 50)
        self.assertEqual(data['tuberia'], self.tuberia_pvc_100.id)
    
    def test_serializar_stock_equipo(self):
        """Prueba: Serializar stock de equipo"""
        serializer = StockEquipoSerializer(self.stock_motor_50hp)
        data = serializer.data
        
        self.assertEqual(data['cantidad'], 3)
        self.assertEqual(data['equipo'], self.motor_bombeo_50hp.id)
