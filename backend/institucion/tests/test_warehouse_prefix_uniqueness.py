"""
Property-based test for warehouse prefix uniqueness.

**Feature: hidroven-organizational-restructuring, Property 4: Warehouse Prefix Uniqueness**
**Validates: Requirements 2.2**

Tests that for any set of regional warehouses, no two warehouses should ever 
have identical three-letter prefix codes.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from hypothesis.extra.django import TestCase as HypothesisTestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.contrib.auth import get_user_model

from institucion.models import (
    Empresa, Vicepresidencia, UnidadOrganizacional, AlmacenRegional
)
from test_utils import PropertyTestMixin, DatabaseTestMixin, TestDataFactory

User = get_user_model()


# Custom strategies for warehouse testing
@st.composite
def valid_warehouse_prefix_strategy(draw):
    """Generate valid warehouse prefixes from predefined list"""
    valid_prefixes = ['ZUL', 'CAR', 'MIR', 'ARA', 'LAR', 'TAC', 'BOL', 'ANZ', 'MON']
    return draw(st.sampled_from(valid_prefixes))


@st.composite
def warehouse_data_strategy(draw):
    """Generate warehouse data for testing"""
    return {
        'nombre': draw(st.text(min_size=1, max_size=200, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -')),
        'prefijo': draw(valid_warehouse_prefix_strategy()),
        'ubicacion': draw(st.text(min_size=1, max_size=200, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ,-')),
        'capacidad_maxima': draw(st.integers(min_value=1, max_value=50000)),
        'activo': draw(st.booleans()),
        'descripcion': draw(st.text(max_size=500)),
        'telefono': draw(st.text(min_size=0, max_size=50, alphabet='0123456789+-() ')),
        'email': draw(st.one_of(st.none(), st.emails())),
    }


@st.composite
def multiple_warehouses_strategy(draw):
    """Generate multiple warehouse data sets for testing uniqueness"""
    num_warehouses = draw(st.integers(min_value=2, max_value=9))  # Max 9 since we have 9 valid prefixes
    warehouses = []
    
    for i in range(num_warehouses):
        warehouse_data = draw(warehouse_data_strategy())
        warehouses.append(warehouse_data)
    
    return warehouses


@st.composite
def organizational_hierarchy_strategy(draw):
    """Generate organizational hierarchy for warehouse testing"""
    empresa_data = {
        'nombre': draw(st.text(min_size=1, max_size=200, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ')),
        'codigo': draw(st.text(min_size=1, max_size=10, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-')),
        'rif': draw(st.text(min_size=0, max_size=30, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-')),
    }
    
    vp_data = {
        'nombre': draw(st.text(min_size=1, max_size=200, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ')),
        'codigo': draw(st.text(min_size=1, max_size=20, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-')),
        'tipo': 'OPERACIONES_HIDRICAS',  # Fixed to ensure warehouses can be created
    }
    
    unidad_data = {
        'nombre': draw(st.text(min_size=1, max_size=200, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ')),
        'codigo': draw(st.text(min_size=1, max_size=30, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-')),
        'tipo': 'ALMACEN',
    }
    
    return {
        'empresa': empresa_data,
        'vicepresidencia': vp_data,
        'unidad_organizacional': unidad_data,
    }


@pytest.mark.property
class WarehousePrefixUniquenessPropertyTest(HypothesisTestCase, PropertyTestMixin, DatabaseTestMixin):
    """
    Property-based test for warehouse prefix uniqueness.
    
    **Feature: hidroven-organizational-restructuring, Property 4: Warehouse Prefix Uniqueness**
    **Validates: Requirements 2.2**
    
    Tests that for any set of regional warehouses, no two warehouses should ever 
    have identical three-letter prefix codes.
    """
    
    def setUp(self):
        """Set up test data"""
        import uuid
        # Create unique identifiers for each test run
        unique_id = str(uuid.uuid4())[:8]
        
        # Create base organizational hierarchy for testing
        self.empresa = Empresa.objects.create(
            nombre=f'Hidroven Test {unique_id}',
            codigo=f'HDV-TEST-{unique_id}',
            rif=f'G-{unique_id}-0'
        )
        
        self.vp_operaciones = Vicepresidencia.objects.create(
            empresa=self.empresa,
            nombre=f'VP Operaciones Test {unique_id}',
            codigo=f'VP-OP-TEST-{unique_id}',
            tipo='OPERACIONES_HIDRICAS'
        )
        
        self.gerencia_almacenes = UnidadOrganizacional.objects.create(
            vicepresidencia=self.vp_operaciones,
            nombre=f'Gerencia de Almacenes Test {unique_id}',
            codigo=f'GER-ALM-TEST-{unique_id}',
            tipo='GERENCIA'
        )
        
        # Create test user
        self.manager = TestDataFactory.create_user(username=f'warehouse_manager_test_{unique_id}')
    
    def create_unidad_organizacional(self, suffix=""):
        """Helper to create unique organizational units"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return UnidadOrganizacional.objects.create(
            vicepresidencia=self.vp_operaciones,
            nombre=f'Unidad Almacén Test {suffix} {unique_id}',
            codigo=f'ALM-TEST-{suffix}-{unique_id}',
            tipo='ALMACEN',
            parent=self.gerencia_almacenes
        )
    
    @given(warehouse_data_strategy())
    @settings(max_examples=100, deadline=None)
    def test_single_warehouse_prefix_uniqueness(self, warehouse_data):
        """
        Property: Any single warehouse with valid data should be created successfully
        and maintain prefix uniqueness.
        """
        # Assume valid data constraints
        assume(len(warehouse_data['nombre'].strip()) > 0)
        assume(len(warehouse_data['ubicacion'].strip()) > 0)
        assume(warehouse_data['capacidad_maxima'] > 0)
        
        # Create organizational unit for this warehouse
        unidad = self.create_unidad_organizacional(suffix=warehouse_data['prefijo'])
        
        # Create warehouse
        almacen = AlmacenRegional.objects.create(
            unidad_organizacional=unidad,
            nombre=warehouse_data['nombre'].strip(),
            prefijo=warehouse_data['prefijo'],
            ubicacion=warehouse_data['ubicacion'].strip(),
            capacidad_maxima=warehouse_data['capacidad_maxima'],
            activo=warehouse_data['activo'],
            manager=self.manager if warehouse_data.get('manager_assigned', False) else None,
            descripcion=warehouse_data.get('descripcion', ''),
            telefono=warehouse_data.get('telefono', ''),
            email=warehouse_data.get('email', '') if warehouse_data.get('email') else '',
        )
        
        # Verify warehouse was created successfully
        self.assertEqual(almacen.prefijo, warehouse_data['prefijo'])
        self.assertEqual(almacen.nombre, warehouse_data['nombre'].strip())
        self.assertEqual(almacen.ubicacion, warehouse_data['ubicacion'].strip())
        self.assertEqual(almacen.capacidad_maxima, warehouse_data['capacidad_maxima'])
        self.assertEqual(almacen.activo, warehouse_data['activo'])
        
        # Verify prefix uniqueness validation method works
        self.assertFalse(AlmacenRegional.validate_prefix_uniqueness(warehouse_data['prefijo']))
        self.assertTrue(AlmacenRegional.validate_prefix_uniqueness(warehouse_data['prefijo'], exclude_id=almacen.id))
        
        # Verify database integrity
        self.assertDatabaseIntegrity(AlmacenRegional)
    
    @given(multiple_warehouses_strategy())
    @settings(max_examples=100, deadline=None)
    def test_multiple_warehouses_prefix_uniqueness_enforcement(self, warehouses_data):
        """
        Property: When creating multiple warehouses, the system should enforce
        prefix uniqueness and prevent duplicate prefixes.
        """
        # Assume we have at least 2 warehouses
        assume(len(warehouses_data) >= 2)
        
        # Filter to valid data
        valid_warehouses = []
        for warehouse_data in warehouses_data:
            if (len(warehouse_data['nombre'].strip()) > 0 and 
                len(warehouse_data['ubicacion'].strip()) > 0 and 
                warehouse_data['capacidad_maxima'] > 0):
                valid_warehouses.append(warehouse_data)
        
        assume(len(valid_warehouses) >= 2)
        
        created_warehouses = []
        used_prefixes = set()
        
        for i, warehouse_data in enumerate(valid_warehouses):
            # Create unique organizational unit for each warehouse
            unidad = self.create_unidad_organizacional(suffix=f"{warehouse_data['prefijo']}-{i}")
            
            if warehouse_data['prefijo'] not in used_prefixes:
                # First warehouse with this prefix should succeed
                almacen = AlmacenRegional.objects.create(
                    unidad_organizacional=unidad,
                    nombre=warehouse_data['nombre'].strip(),
                    prefijo=warehouse_data['prefijo'],
                    ubicacion=warehouse_data['ubicacion'].strip(),
                    capacidad_maxima=warehouse_data['capacidad_maxima'],
                    activo=warehouse_data['activo'],
                    manager=self.manager,
                )
                created_warehouses.append(almacen)
                used_prefixes.add(warehouse_data['prefijo'])
            else:
                # Subsequent warehouses with same prefix should fail
                with self.assertRaises(ValidationError):
                    AlmacenRegional.objects.create(
                        unidad_organizacional=unidad,
                        nombre=warehouse_data['nombre'].strip(),
                        prefijo=warehouse_data['prefijo'],  # Duplicate prefix
                        ubicacion=warehouse_data['ubicacion'].strip(),
                        capacidad_maxima=warehouse_data['capacidad_maxima'],
                        activo=warehouse_data['activo'],
                        manager=self.manager,
                    )
        
        # Verify all created warehouses have unique prefixes
        created_prefixes = [w.prefijo for w in created_warehouses]
        self.assertEqual(len(created_prefixes), len(set(created_prefixes)), 
                        "All created warehouses should have unique prefixes")
        
        # Verify database integrity
        self.assertDatabaseIntegrity(AlmacenRegional)
    
    @given(st.lists(valid_warehouse_prefix_strategy(), min_size=2, max_size=9, unique=True))
    @settings(max_examples=100, deadline=None)
    def test_all_valid_prefixes_can_be_used_uniquely(self, unique_prefixes):
        """
        Property: All valid prefixes should be usable exactly once,
        and the system should prevent reuse of any prefix.
        """
        created_warehouses = []
        
        # Create warehouses with unique prefixes
        for i, prefix in enumerate(unique_prefixes):
            unidad = self.create_unidad_organizacional(suffix=f"{prefix}-{i}")
            
            almacen = AlmacenRegional.objects.create(
                unidad_organizacional=unidad,
                nombre=f'Almacén Regional {prefix}',
                prefijo=prefix,
                ubicacion=f'Ubicación {prefix}',
                capacidad_maxima=1000,
                activo=True,
                manager=self.manager,
            )
            created_warehouses.append(almacen)
        
        # Verify all warehouses were created successfully
        self.assertEqual(len(created_warehouses), len(unique_prefixes))
        
        # Verify all prefixes are unique
        created_prefixes = [w.prefijo for w in created_warehouses]
        self.assertEqual(len(created_prefixes), len(set(created_prefixes)))
        
        # Try to create another warehouse with each used prefix - should fail
        for prefix in unique_prefixes:
            unidad = self.create_unidad_organizacional(suffix=f"duplicate-{prefix}")
            
            with self.assertRaises(ValidationError):
                AlmacenRegional.objects.create(
                    unidad_organizacional=unidad,
                    nombre=f'Duplicate Almacén {prefix}',
                    prefijo=prefix,  # This should fail due to uniqueness
                    ubicacion=f'Duplicate Location {prefix}',
                    capacidad_maxima=1000,
                    activo=True,
                    manager=self.manager,
                )
        
        # Verify database integrity
        self.assertDatabaseIntegrity(AlmacenRegional)
    
    @given(organizational_hierarchy_strategy(), warehouse_data_strategy())
    @settings(max_examples=100, deadline=None)
    def test_prefix_uniqueness_across_different_organizational_units(self, hierarchy_data, warehouse_data):
        """
        Property: Prefix uniqueness should be enforced across all organizational units,
        not just within a single unit.
        """
        # Assume valid data constraints
        assume(len(warehouse_data['nombre'].strip()) > 0)
        assume(len(warehouse_data['ubicacion'].strip()) > 0)
        assume(warehouse_data['capacidad_maxima'] > 0)
        assume(len(hierarchy_data['empresa']['nombre'].strip()) > 0)
        assume(len(hierarchy_data['vicepresidencia']['nombre'].strip()) > 0)
        assume(len(hierarchy_data['unidad_organizacional']['nombre'].strip()) > 0)
        
        # Create alternative organizational hierarchy
        import uuid
        unique_id2 = str(uuid.uuid4())[:8]
        empresa2 = Empresa.objects.create(
            nombre=hierarchy_data['empresa']['nombre'].strip(),
            codigo=f"{hierarchy_data['empresa']['codigo']}-ALT-{unique_id2}",
            rif=f"{hierarchy_data['empresa']['rif']}-{unique_id2}"
        )
        
        vp2 = Vicepresidencia.objects.create(
            empresa=empresa2,
            nombre=hierarchy_data['vicepresidencia']['nombre'].strip(),
            codigo=f"{hierarchy_data['vicepresidencia']['codigo']}-ALT-{unique_id2}",
            tipo=hierarchy_data['vicepresidencia']['tipo']
        )
        
        unidad2 = UnidadOrganizacional.objects.create(
            vicepresidencia=vp2,
            nombre=hierarchy_data['unidad_organizacional']['nombre'].strip(),
            codigo=f"{hierarchy_data['unidad_organizacional']['codigo']}-ALT-{unique_id2}",
            tipo=hierarchy_data['unidad_organizacional']['tipo']
        )
        
        # Create first warehouse in original hierarchy
        unidad1 = self.create_unidad_organizacional(suffix="first")
        almacen1 = AlmacenRegional.objects.create(
            unidad_organizacional=unidad1,
            nombre=warehouse_data['nombre'].strip(),
            prefijo=warehouse_data['prefijo'],
            ubicacion=warehouse_data['ubicacion'].strip(),
            capacidad_maxima=warehouse_data['capacidad_maxima'],
            activo=warehouse_data['activo'],
            manager=self.manager,
        )
        
        # Try to create second warehouse with same prefix in different hierarchy
        with self.assertRaises(ValidationError):
            AlmacenRegional.objects.create(
                unidad_organizacional=unidad2,
                nombre=f"Different {warehouse_data['nombre'].strip()}",
                prefijo=warehouse_data['prefijo'],  # Same prefix should fail
                ubicacion=f"Different {warehouse_data['ubicacion'].strip()}",
                capacidad_maxima=warehouse_data['capacidad_maxima'],
                activo=warehouse_data['activo'],
                manager=self.manager,
            )
        
        # Verify only one warehouse exists with this prefix
        warehouses_with_prefix = AlmacenRegional.objects.filter(prefijo=warehouse_data['prefijo'])
        self.assertEqual(warehouses_with_prefix.count(), 1)
        self.assertEqual(warehouses_with_prefix.first(), almacen1)
        
        # Verify database integrity
        self.assertDatabaseIntegrity(AlmacenRegional)
    
    @given(warehouse_data_strategy())
    @settings(max_examples=100, deadline=None)
    def test_prefix_uniqueness_validation_method_consistency(self, warehouse_data):
        """
        Property: The validate_prefix_uniqueness class method should be consistent
        with actual database constraints and model validation.
        """
        # Assume valid data constraints
        assume(len(warehouse_data['nombre'].strip()) > 0)
        assume(len(warehouse_data['ubicacion'].strip()) > 0)
        assume(warehouse_data['capacidad_maxima'] > 0)
        
        prefix = warehouse_data['prefijo']
        
        # Initially, prefix should be available
        self.assertTrue(AlmacenRegional.validate_prefix_uniqueness(prefix))
        
        # Create warehouse
        unidad = self.create_unidad_organizacional(suffix=prefix)
        almacen = AlmacenRegional.objects.create(
            unidad_organizacional=unidad,
            nombre=warehouse_data['nombre'].strip(),
            prefijo=prefix,
            ubicacion=warehouse_data['ubicacion'].strip(),
            capacidad_maxima=warehouse_data['capacidad_maxima'],
            activo=warehouse_data['activo'],
            manager=self.manager,
        )
        
        # After creation, prefix should not be available
        self.assertFalse(AlmacenRegional.validate_prefix_uniqueness(prefix))
        
        # But should be available when excluding the current warehouse
        self.assertTrue(AlmacenRegional.validate_prefix_uniqueness(prefix, exclude_id=almacen.id))
        
        # Verify get_by_prefix method works correctly
        if almacen.activo:
            found_warehouse = AlmacenRegional.get_by_prefix(prefix)
            self.assertEqual(found_warehouse, almacen)
        else:
            # Inactive warehouses should not be found by get_by_prefix
            found_warehouse = AlmacenRegional.get_by_prefix(prefix)
            self.assertIsNone(found_warehouse)
        
        # Verify non-existent prefix returns None
        non_existent = AlmacenRegional.get_by_prefix('XXX')
        self.assertIsNone(non_existent)
        
        # Verify database integrity
        self.assertDatabaseIntegrity(AlmacenRegional)
    
    @given(st.integers(min_value=1, max_value=9))
    @settings(max_examples=100, deadline=None)
    def test_maximum_warehouse_capacity_with_unique_prefixes(self, num_warehouses):
        """
        Property: The system should support up to 9 warehouses (one for each valid prefix)
        and enforce uniqueness across all of them.
        """
        valid_prefixes = ['ZUL', 'CAR', 'MIR', 'ARA', 'LAR', 'TAC', 'BOL', 'ANZ', 'MON']
        selected_prefixes = valid_prefixes[:num_warehouses]
        
        created_warehouses = []
        
        # Create warehouses up to the specified number
        for i, prefix in enumerate(selected_prefixes):
            unidad = self.create_unidad_organizacional(suffix=f"{prefix}-{i}")
            
            almacen = AlmacenRegional.objects.create(
                unidad_organizacional=unidad,
                nombre=f'Almacén Regional {prefix}',
                prefijo=prefix,
                ubicacion=f'Ubicación {prefix}',
                capacidad_maxima=1000 + i * 100,  # Vary capacity
                activo=True,
                manager=self.manager,
            )
            created_warehouses.append(almacen)
        
        # Verify correct number of warehouses created
        self.assertEqual(len(created_warehouses), num_warehouses)
        
        # Verify all prefixes are unique
        created_prefixes = [w.prefijo for w in created_warehouses]
        self.assertEqual(len(created_prefixes), len(set(created_prefixes)))
        
        # Verify all created prefixes are from valid set
        for prefix in created_prefixes:
            self.assertIn(prefix, valid_prefixes)
        
        # Verify get_all_active returns all created warehouses
        active_warehouses = AlmacenRegional.get_all_active()
        self.assertEqual(active_warehouses.count(), num_warehouses)
        
        # Verify database integrity
        self.assertDatabaseIntegrity(AlmacenRegional)