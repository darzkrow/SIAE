"""
Unit tests for AlmacenRegional model.

Tests the functionality of the regional warehouse model including:
- Model creation and validation
- Unique prefix constraints
- Relationship to organizational hierarchy
- Business logic methods
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from institucion.models import (
    Empresa, Vicepresidencia, UnidadOrganizacional, AlmacenRegional
)

User = get_user_model()


class AlmacenRegionalModelTest(TestCase):
    """Test cases for AlmacenRegional model"""

    def setUp(self):
        """Set up test data"""
        # Create organizational hierarchy
        self.empresa = Empresa.objects.create(
            nombre='Hidroven Test',
            codigo='HDV-TEST',
            rif='G-20000000-0'
        )
        
        self.vp_operaciones = Vicepresidencia.objects.create(
            empresa=self.empresa,
            nombre='VP Operaciones Test',
            codigo='VP-OP-TEST',
            tipo='OPERACIONES_HIDRICAS'
        )
        
        self.gerencia_almacenes = UnidadOrganizacional.objects.create(
            vicepresidencia=self.vp_operaciones,
            nombre='Gerencia de Almacenes Test',
            codigo='GER-ALM-TEST',
            tipo='GERENCIA'
        )
        
        self.unidad_almacen = UnidadOrganizacional.objects.create(
            vicepresidencia=self.vp_operaciones,
            nombre='Unidad Almacén Test',
            codigo='ALM-TEST',
            tipo='ALMACEN',
            parent=self.gerencia_almacenes
        )
        
        # Create test user
        self.manager = User.objects.create_user(
            username='manager_test',
            email='manager@test.com',
            password='testpass123'
        )

    def test_create_almacen_regional_valid(self):
        """Test creating a valid AlmacenRegional"""
        almacen = AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad_almacen,
            nombre='Almacén Regional Test',
            prefijo='ZUL',
            ubicacion='Maracaibo, Zulia',
            manager=self.manager,
            capacidad_maxima=5000
        )
        
        self.assertEqual(almacen.nombre, 'Almacén Regional Test')
        self.assertEqual(almacen.prefijo, 'ZUL')
        self.assertEqual(almacen.ubicacion, 'Maracaibo, Zulia')
        self.assertEqual(almacen.manager, self.manager)
        self.assertEqual(almacen.capacidad_maxima, 5000)
        self.assertTrue(almacen.activo)
        self.assertIsNotNone(almacen.fecha_creacion)
        self.assertIsNotNone(almacen.fecha_actualizacion)

    def test_unique_prefix_constraint(self):
        """Test that prefix must be unique"""
        # Create first warehouse
        AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad_almacen,
            nombre='Almacén Regional 1',
            prefijo='ZUL',
            ubicacion='Maracaibo, Zulia'
        )
        
        # Create second organizational unit
        unidad_almacen_2 = UnidadOrganizacional.objects.create(
            vicepresidencia=self.vp_operaciones,
            nombre='Unidad Almacén Test 2',
            codigo='ALM-TEST-2',
            tipo='ALMACEN',
            parent=self.gerencia_almacenes
        )
        
        # Try to create second warehouse with same prefix
        # This should raise ValidationError due to our custom validation
        with self.assertRaises(ValidationError):
            AlmacenRegional.objects.create(
                unidad_organizacional=unidad_almacen_2,
                nombre='Almacén Regional 2',
                prefijo='ZUL',  # Same prefix should fail
                ubicacion='Valencia, Carabobo'
            )

    def test_invalid_prefix_validation(self):
        """Test validation of invalid prefixes"""
        almacen = AlmacenRegional(
            unidad_organizacional=self.unidad_almacen,
            nombre='Almacén Regional Test',
            prefijo='XXX',  # Invalid prefix
            ubicacion='Test Location'
        )
        
        with self.assertRaises(ValidationError) as context:
            almacen.full_clean()
        
        self.assertIn('prefijo', context.exception.message_dict)

    def test_valid_prefixes(self):
        """Test all valid prefixes can be used"""
        valid_prefixes = ['ZUL', 'CAR', 'MIR', 'ARA', 'LAR', 'TAC', 'BOL', 'ANZ', 'MON']
        
        for i, prefix in enumerate(valid_prefixes):
            # Create unique organizational unit for each warehouse
            unidad = UnidadOrganizacional.objects.create(
                vicepresidencia=self.vp_operaciones,
                nombre=f'Unidad Almacén {prefix}',
                codigo=f'ALM-{prefix}',
                tipo='ALMACEN',
                parent=self.gerencia_almacenes
            )
            
            almacen = AlmacenRegional.objects.create(
                unidad_organizacional=unidad,
                nombre=f'Almacén Regional {prefix}',
                prefijo=prefix,
                ubicacion=f'Location {prefix}'
            )
            
            self.assertEqual(almacen.prefijo, prefix)

    def test_vp_operaciones_validation(self):
        """Test that warehouse must belong to VP Operaciones"""
        # Create VP Comercialización
        vp_comercializacion = Vicepresidencia.objects.create(
            empresa=self.empresa,
            nombre='VP Comercialización Test',
            codigo='VP-COM-TEST',
            tipo='COMERCIALIZACION'
        )
        
        unidad_comercial = UnidadOrganizacional.objects.create(
            vicepresidencia=vp_comercializacion,
            nombre='Unidad Comercial',
            codigo='COM-TEST',
            tipo='GERENCIA'
        )
        
        almacen = AlmacenRegional(
            unidad_organizacional=unidad_comercial,
            nombre='Almacén Test',
            prefijo='CAR',
            ubicacion='Test Location'
        )
        
        with self.assertRaises(ValidationError) as context:
            almacen.full_clean()
        
        self.assertIn('unidad_organizacional', context.exception.message_dict)

    def test_str_representation(self):
        """Test string representation of AlmacenRegional"""
        almacen = AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad_almacen,
            nombre='Almacén Regional Zulia',
            prefijo='ZUL',
            ubicacion='Maracaibo, Zulia'
        )
        
        self.assertEqual(str(almacen), 'ZUL - Almacén Regional Zulia')

    def test_get_full_path(self):
        """Test hierarchical path generation"""
        almacen = AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad_almacen,
            nombre='Almacén Regional Zulia',
            prefijo='ZUL',
            ubicacion='Maracaibo, Zulia'
        )
        
        path = almacen.get_full_path()
        self.assertIn('Hidroven Test', path)
        self.assertIn('VP Operaciones Test', path)
        self.assertIn('Almacén Regional Zulia', path)

    def test_get_by_prefix(self):
        """Test getting warehouse by prefix"""
        almacen = AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad_almacen,
            nombre='Almacén Regional Zulia',
            prefijo='ZUL',
            ubicacion='Maracaibo, Zulia'
        )
        
        found_almacen = AlmacenRegional.get_by_prefix('ZUL')
        self.assertEqual(found_almacen, almacen)
        
        not_found = AlmacenRegional.get_by_prefix('XXX')
        self.assertIsNone(not_found)

    def test_get_all_active(self):
        """Test getting all active warehouses"""
        # Create active warehouse
        active_almacen = AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad_almacen,
            nombre='Almacén Activo',
            prefijo='ZUL',
            ubicacion='Test Location',
            activo=True
        )
        
        # Create inactive warehouse
        unidad_almacen_2 = UnidadOrganizacional.objects.create(
            vicepresidencia=self.vp_operaciones,
            nombre='Unidad Almacén 2',
            codigo='ALM-TEST-2',
            tipo='ALMACEN',
            parent=self.gerencia_almacenes
        )
        
        AlmacenRegional.objects.create(
            unidad_organizacional=unidad_almacen_2,
            nombre='Almacén Inactivo',
            prefijo='CAR',
            ubicacion='Test Location 2',
            activo=False
        )
        
        active_warehouses = AlmacenRegional.get_all_active()
        self.assertEqual(active_warehouses.count(), 1)
        self.assertEqual(active_warehouses.first(), active_almacen)

    def test_validate_prefix_uniqueness(self):
        """Test prefix uniqueness validation method"""
        # Test with no existing warehouses
        self.assertTrue(AlmacenRegional.validate_prefix_uniqueness('ZUL'))
        
        # Create warehouse
        almacen = AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad_almacen,
            nombre='Almacén Regional Zulia',
            prefijo='ZUL',
            ubicacion='Maracaibo, Zulia'
        )
        
        # Test with existing warehouse
        self.assertFalse(AlmacenRegional.validate_prefix_uniqueness('ZUL'))
        
        # Test excluding current warehouse
        self.assertTrue(AlmacenRegional.validate_prefix_uniqueness('ZUL', exclude_id=almacen.id))

    def test_capacity_methods(self):
        """Test capacity-related methods"""
        almacen = AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad_almacen,
            nombre='Almacén Regional Test',
            prefijo='ZUL',
            ubicacion='Test Location',
            capacidad_maxima=1000
        )
        
        # Test current capacity usage (should be 0 for now)
        self.assertEqual(almacen.get_current_capacity_usage(), 0)
        
        # Test is at capacity
        self.assertFalse(almacen.is_at_capacity())
        
        # Test available capacity
        self.assertEqual(almacen.get_available_capacity(), 1000)

    def test_manager_assignment(self):
        """Test manager assignment and relationship"""
        almacen = AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad_almacen,
            nombre='Almacén Regional Test',
            prefijo='ZUL',
            ubicacion='Test Location',
            manager=self.manager
        )
        
        self.assertEqual(almacen.manager, self.manager)
        
        # Test reverse relationship
        managed_warehouses = self.manager.almacenes_gestionados.all()
        self.assertIn(almacen, managed_warehouses)

    def test_optional_fields(self):
        """Test optional fields functionality"""
        almacen = AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad_almacen,
            nombre='Almacén Regional Test',
            prefijo='ZUL',
            ubicacion='Test Location',
            descripcion='Test description',
            telefono='+58-261-1234567',
            email='almacen@test.com'
        )
        
        self.assertEqual(almacen.descripcion, 'Test description')
        self.assertEqual(almacen.telefono, '+58-261-1234567')
        self.assertEqual(almacen.email, 'almacen@test.com')

    def test_minimum_capacity_validation(self):
        """Test minimum capacity validation"""
        with self.assertRaises(ValidationError):
            almacen = AlmacenRegional(
                unidad_organizacional=self.unidad_almacen,
                nombre='Almacén Regional Test',
                prefijo='ZUL',
                ubicacion='Test Location',
                capacidad_maxima=0  # Should fail validation
            )
            almacen.full_clean()