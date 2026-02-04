"""
Test the hierarchical organizational structure setup.

This test verifies that the management command creates the correct
organizational hierarchy as specified in the design document.
"""

from django.test import TestCase
from django.core.management import call_command
from django.db import transaction
from .models import Empresa, Vicepresidencia, UnidadOrganizacional


class HierarchySetupTest(TestCase):
    """Test the setup_hidroven_hierarchy management command"""
    
    def test_setup_complete_hierarchy(self):
        """Test that the management command creates the complete hierarchy"""
        # Run the management command
        call_command('setup_hidroven_hierarchy')
        
        # Verify empresa was created
        self.assertEqual(Empresa.objects.count(), 1)
        hidroven = Empresa.objects.get(codigo='HDV')
        self.assertEqual(hidroven.nombre, 'Hidroven')
        self.assertEqual(hidroven.rif, 'G-20000000-0')
        
        # Verify vicepresidencias were created
        self.assertEqual(Vicepresidencia.objects.count(), 3)
        
        vp_comercial = Vicepresidencia.objects.get(codigo='VP-COM')
        self.assertEqual(vp_comercial.tipo, 'COMERCIALIZACION')
        self.assertEqual(vp_comercial.empresa, hidroven)
        
        vp_operaciones = Vicepresidencia.objects.get(codigo='VP-OH')
        self.assertEqual(vp_operaciones.tipo, 'OPERACIONES_HIDRICAS')
        
        vp_administrativa = Vicepresidencia.objects.get(codigo='VP-ADM')
        self.assertEqual(vp_administrativa.tipo, 'ADMINISTRATIVA')
        
        # Verify organizational units were created
        # VP Comercialización should have 3 gerencias
        comercial_units = UnidadOrganizacional.objects.filter(
            vicepresidencia=vp_comercial
        )
        self.assertEqual(comercial_units.count(), 3)
        
        # VP Operaciones should have 4 gerencias + 9 regional warehouses
        operaciones_units = UnidadOrganizacional.objects.filter(
            vicepresidencia=vp_operaciones
        )
        self.assertEqual(operaciones_units.count(), 13)  # 4 gerencias + 9 almacenes
        
        # VP Administrativa should have 4 gerencias
        administrativa_units = UnidadOrganizacional.objects.filter(
            vicepresidencia=vp_administrativa
        )
        self.assertEqual(administrativa_units.count(), 4)
        
        # Verify regional warehouses are under Gerencia de Almacenes
        gerencia_almacenes = UnidadOrganizacional.objects.get(codigo='GER-OP-ALM')
        regional_warehouses = gerencia_almacenes.get_children()
        self.assertEqual(regional_warehouses.count(), 9)
        
        # Verify specific warehouse codes
        warehouse_codes = [
            'ALM-ZUL', 'ALM-CAR', 'ALM-MIR', 'ALM-ARA', 'ALM-LAR',
            'ALM-TAC', 'ALM-BOL', 'ALM-ANZ', 'ALM-MON'
        ]
        
        for code in warehouse_codes:
            warehouse = UnidadOrganizacional.objects.get(codigo=code)
            self.assertEqual(warehouse.tipo, 'ALMACEN')
            self.assertEqual(warehouse.parent, gerencia_almacenes)
    
    def test_hierarchy_paths(self):
        """Test hierarchical path generation"""
        call_command('setup_hidroven_hierarchy')
        
        # Test empresa path
        hidroven = Empresa.objects.get(codigo='HDV')
        self.assertEqual(hidroven.get_full_path(), 'Hidroven')
        
        # Test vicepresidencia path
        vp_operaciones = Vicepresidencia.objects.get(codigo='VP-OH')
        expected_vp_path = 'Hidroven → Vicepresidencia de Operaciones Hídricas'
        self.assertEqual(vp_operaciones.get_full_path(), expected_vp_path)
        
        # Test gerencia path
        gerencia_almacenes = UnidadOrganizacional.objects.get(codigo='GER-OP-ALM')
        expected_gerencia_path = 'Hidroven → Vicepresidencia de Operaciones Hídricas → Gerencia de Almacenes'
        self.assertEqual(gerencia_almacenes.get_full_path(), expected_gerencia_path)
        
        # Test regional warehouse path
        almacen_zulia = UnidadOrganizacional.objects.get(codigo='ALM-ZUL')
        expected_almacen_path = 'Hidroven → Vicepresidencia de Operaciones Hídricas → Gerencia de Almacenes → Almacén Regional Zulia'
        self.assertEqual(almacen_zulia.get_full_path(), expected_almacen_path)
    
    def test_reset_functionality(self):
        """Test the reset functionality of the management command"""
        # Create initial hierarchy
        call_command('setup_hidroven_hierarchy')
        
        # Verify data exists
        self.assertEqual(Empresa.objects.count(), 1)
        self.assertEqual(Vicepresidencia.objects.count(), 3)
        self.assertTrue(UnidadOrganizacional.objects.count() > 0)
        
        # Reset and recreate
        call_command('setup_hidroven_hierarchy', '--reset')
        
        # Verify data still exists (recreated)
        self.assertEqual(Empresa.objects.count(), 1)
        self.assertEqual(Vicepresidencia.objects.count(), 3)
        self.assertTrue(UnidadOrganizacional.objects.count() > 0)
    
    def test_idempotent_execution(self):
        """Test that running the command multiple times doesn't create duplicates"""
        # Run command twice
        call_command('setup_hidroven_hierarchy')
        call_command('setup_hidroven_hierarchy')
        
        # Verify no duplicates were created
        self.assertEqual(Empresa.objects.count(), 1)
        self.assertEqual(Vicepresidencia.objects.count(), 3)
        
        # Count should remain the same
        expected_units = 3 + 13 + 4  # VP-COM + VP-OH + VP-ADM units
        self.assertEqual(UnidadOrganizacional.objects.count(), expected_units)