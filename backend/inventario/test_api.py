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
        """
        Archivo de pruebas API archivado. Original movido a
        `inventario/archived_tests/inventario__test_api.py`.
        Stub para evitar ejecución accidental.
        """

        __all__ = []

