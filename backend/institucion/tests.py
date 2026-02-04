from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from .models import Empresa, Vicepresidencia, UnidadOrganizacional

User = get_user_model()


class EmpresaModelTest(TestCase):
    """Test cases for the Empresa hierarchical model"""
    
    def setUp(self):
        """Set up test data"""
        self.empresa_data = {
            'nombre': 'Hidroven',
            'codigo': 'HDV',
            'rif': 'G-20000000-0',
            'direccion': 'Caracas, Venezuela',
            'telefono': '+58-212-1234567',
            'email': 'info@hidroven.gob.ve'
        }
    
    def test_create_empresa(self):
        """Test creating a basic empresa"""
        empresa = Empresa.objects.create(**self.empresa_data)
        
        self.assertEqual(empresa.nombre, 'Hidroven')
        self.assertEqual(empresa.codigo, 'HDV')
        self.assertEqual(empresa.rif, 'G-20000000-0')
        self.assertTrue(empresa.activo)
        self.assertIsNotNone(empresa.fecha_creacion)
        self.assertIsNotNone(empresa.fecha_actualizacion)
    
    def test_empresa_unique_nombre_constraint(self):
        """Test unique constraint on nombre"""
        Empresa.objects.create(**self.empresa_data)
        
        with self.assertRaises(IntegrityError):
            Empresa.objects.create(
                nombre='Hidroven',  # Duplicate nombre
                codigo='HDV2',
                rif='G-20000001-0'
            )
    
    def test_empresa_unique_codigo_constraint(self):
        """Test unique constraint on codigo"""
        Empresa.objects.create(**self.empresa_data)
        
        with self.assertRaises(IntegrityError):
            Empresa.objects.create(
                nombre='Hidroven 2',
                codigo='HDV',  # Duplicate codigo
                rif='G-20000001-0'
            )
    
    def test_empresa_hierarchy(self):
        """Test hierarchical relationships"""
        parent = Empresa.objects.create(**self.empresa_data)
        
        child_data = {
            'nombre': 'Hidroven Regional',
            'codigo': 'HDV-REG',
            'rif': 'G-20000001-0',
            'parent': parent
        }
        child = Empresa.objects.create(**child_data)
        
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.get_children())
        self.assertEqual(child.get_level(), 1)
        self.assertEqual(parent.get_level(), 0)
    
    def test_get_full_path(self):
        """Test full hierarchical path generation"""
        parent = Empresa.objects.create(**self.empresa_data)
        child = Empresa.objects.create(
            nombre='Hidroven Regional',
            codigo='HDV-REG',
            parent=parent
        )
        
        self.assertEqual(parent.get_full_path(), 'Hidroven')
        self.assertEqual(child.get_full_path(), 'Hidroven → Hidroven Regional')
    
    def test_empresa_str_representation(self):
        """Test string representation"""
        empresa = Empresa.objects.create(**self.empresa_data)
        self.assertEqual(str(empresa), 'Hidroven')


class VicepresidenciaModelTest(TestCase):
    """Test cases for the Vicepresidencia hierarchical model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.empresa = Empresa.objects.create(
            nombre='Hidroven',
            codigo='HDV',
            rif='G-20000000-0'
        )
        
        self.vp_data = {
            'empresa': self.empresa,
            'nombre': 'Vicepresidencia de Operaciones Hídricas',
            'codigo': 'VP-OH',
            'tipo': 'OPERACIONES_HIDRICAS',
            'descripcion': 'Responsable de las operaciones hídricas',
            'responsable': self.user
        }
    
    def test_create_vicepresidencia(self):
        """Test creating a vicepresidencia"""
        vp = Vicepresidencia.objects.create(**self.vp_data)
        
        self.assertEqual(vp.nombre, 'Vicepresidencia de Operaciones Hídricas')
        self.assertEqual(vp.codigo, 'VP-OH')
        self.assertEqual(vp.tipo, 'OPERACIONES_HIDRICAS')
        self.assertEqual(vp.empresa, self.empresa)
        self.assertEqual(vp.responsable, self.user)
        self.assertTrue(vp.activo)
    
    def test_vicepresidencia_choices(self):
        """Test VP type choices"""
        valid_types = ['COMERCIALIZACION', 'OPERACIONES_HIDRICAS', 'ADMINISTRATIVA']
        
        for vp_type in valid_types:
            vp = Vicepresidencia.objects.create(
                empresa=self.empresa,
                nombre=f'VP {vp_type}',
                codigo=f'VP-{vp_type[:3]}',
                tipo=vp_type
            )
            self.assertEqual(vp.tipo, vp_type)
    
    def test_vicepresidencia_unique_constraints(self):
        """Test unique constraints"""
        Vicepresidencia.objects.create(**self.vp_data)
        
        # Test unique codigo within empresa
        with self.assertRaises(IntegrityError):
            Vicepresidencia.objects.create(
                empresa=self.empresa,
                nombre='VP Comercialización',
                codigo='VP-OH',  # Duplicate codigo
                tipo='COMERCIALIZACION'
            )
    
    def test_vicepresidencia_hierarchy(self):
        """Test hierarchical relationships within VP"""
        parent_vp = Vicepresidencia.objects.create(**self.vp_data)
        
        child_vp = Vicepresidencia.objects.create(
            empresa=self.empresa,
            nombre='Sub-VP Operaciones',
            codigo='SUB-VP-OH',
            tipo='OPERACIONES_HIDRICAS',
            parent=parent_vp
        )
        
        self.assertEqual(child_vp.parent, parent_vp)
        self.assertIn(child_vp, parent_vp.get_children())
    
    def test_get_full_path(self):
        """Test full hierarchical path generation"""
        vp = Vicepresidencia.objects.create(**self.vp_data)
        expected_path = 'Hidroven → Vicepresidencia de Operaciones Hídricas'
        self.assertEqual(vp.get_full_path(), expected_path)
    
    def test_vicepresidencia_str_representation(self):
        """Test string representation"""
        vp = Vicepresidencia.objects.create(**self.vp_data)
        expected_str = 'Vicepresidencia de Operaciones Hídricas - Hidroven'
        self.assertEqual(str(vp), expected_str)


class UnidadOrganizacionalModelTest(TestCase):
    """Test cases for the UnidadOrganizacional hierarchical model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.empresa = Empresa.objects.create(
            nombre='Hidroven',
            codigo='HDV'
        )
        
        self.vicepresidencia = Vicepresidencia.objects.create(
            empresa=self.empresa,
            nombre='VP Operaciones Hídricas',
            codigo='VP-OH',
            tipo='OPERACIONES_HIDRICAS'
        )
        
        self.unidad_data = {
            'vicepresidencia': self.vicepresidencia,
            'nombre': 'Gerencia de Almacenes',
            'codigo': 'GER-ALM',
            'tipo': 'GERENCIA',
            'descripcion': 'Gerencia responsable de los almacenes regionales',
            'ubicacion': 'Caracas',
            'responsable': self.user
        }
    
    def test_create_unidad_organizacional(self):
        """Test creating a unidad organizacional"""
        unidad = UnidadOrganizacional.objects.create(**self.unidad_data)
        
        self.assertEqual(unidad.nombre, 'Gerencia de Almacenes')
        self.assertEqual(unidad.codigo, 'GER-ALM')
        self.assertEqual(unidad.tipo, 'GERENCIA')
        self.assertEqual(unidad.vicepresidencia, self.vicepresidencia)
        self.assertEqual(unidad.responsable, self.user)
        self.assertEqual(unidad.ubicacion, 'Caracas')
        self.assertTrue(unidad.activo)
    
    def test_unidad_organizacional_choices(self):
        """Test organizational unit type choices"""
        valid_types = [
            'GERENCIA', 'COORDINACION', 'DEPARTAMENTO', 'DIVISION',
            'SECCION', 'OFICINA', 'ALMACEN', 'PLANTA', 'ESTACION'
        ]
        
        for i, unit_type in enumerate(valid_types):
            unidad = UnidadOrganizacional.objects.create(
                vicepresidencia=self.vicepresidencia,
                nombre=f'Unidad {unit_type}',
                codigo=f'UN-{i:02d}',
                tipo=unit_type
            )
            self.assertEqual(unidad.tipo, unit_type)
    
    def test_unidad_organizacional_unique_constraints(self):
        """Test unique constraints"""
        UnidadOrganizacional.objects.create(**self.unidad_data)
        
        # Test unique codigo within vicepresidencia
        with self.assertRaises(IntegrityError):
            UnidadOrganizacional.objects.create(
                vicepresidencia=self.vicepresidencia,
                nombre='Coordinación de Almacenes',
                codigo='GER-ALM',  # Duplicate codigo
                tipo='COORDINACION'
            )
    
    def test_unidad_organizacional_hierarchy(self):
        """Test hierarchical relationships within unidad"""
        parent_unidad = UnidadOrganizacional.objects.create(**self.unidad_data)
        
        child_unidad = UnidadOrganizacional.objects.create(
            vicepresidencia=self.vicepresidencia,
            nombre='Coordinación Almacén Zulia',
            codigo='COORD-ALM-ZUL',
            tipo='COORDINACION',
            parent=parent_unidad
        )
        
        self.assertEqual(child_unidad.parent, parent_unidad)
        self.assertIn(child_unidad, parent_unidad.get_children())
    
    def test_get_full_path(self):
        """Test full hierarchical path generation"""
        unidad = UnidadOrganizacional.objects.create(**self.unidad_data)
        expected_path = 'Hidroven → VP Operaciones Hídricas → Gerencia de Almacenes'
        self.assertEqual(unidad.get_full_path(), expected_path)
    
    def test_unidad_organizacional_str_representation(self):
        """Test string representation"""
        unidad = UnidadOrganizacional.objects.create(**self.unidad_data)
        expected_str = 'Gerencia de Almacenes - VP Operaciones Hídricas'
        self.assertEqual(str(unidad), expected_str)


class HierarchicalIntegrationTest(TestCase):
    """Integration tests for the complete hierarchical structure"""
    
    def setUp(self):
        """Set up complete hierarchical structure"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create empresa
        self.empresa = Empresa.objects.create(
            nombre='Hidroven',
            codigo='HDV',
            rif='G-20000000-0'
        )
        
        # Create vicepresidencias
        self.vp_operaciones = Vicepresidencia.objects.create(
            empresa=self.empresa,
            nombre='VP Operaciones Hídricas',
            codigo='VP-OH',
            tipo='OPERACIONES_HIDRICAS'
        )
        
        self.vp_comercial = Vicepresidencia.objects.create(
            empresa=self.empresa,
            nombre='VP Comercialización',
            codigo='VP-COM',
            tipo='COMERCIALIZACION'
        )
        
        # Create unidades organizacionales
        self.gerencia_almacenes = UnidadOrganizacional.objects.create(
            vicepresidencia=self.vp_operaciones,
            nombre='Gerencia de Almacenes',
            codigo='GER-ALM',
            tipo='GERENCIA'
        )
        
        self.almacen_zulia = UnidadOrganizacional.objects.create(
            vicepresidencia=self.vp_operaciones,
            nombre='Almacén Regional Zulia',
            codigo='ALM-ZUL',
            tipo='ALMACEN',
            parent=self.gerencia_almacenes
        )
    
    def test_complete_hierarchy_structure(self):
        """Test the complete hierarchical structure"""
        # Test empresa level
        self.assertEqual(self.empresa.get_level(), 0)
        self.assertEqual(self.empresa.vicepresidencias.count(), 2)
        
        # Test vicepresidencia level
        self.assertEqual(self.vp_operaciones.get_level(), 0)  # VP is root in its own tree
        self.assertEqual(self.vp_operaciones.unidades_organizacionales.count(), 2)
        
        # Test unidad organizacional level
        self.assertEqual(self.gerencia_almacenes.get_level(), 0)  # Root in unidad tree
        self.assertEqual(self.almacen_zulia.get_level(), 1)  # Child of gerencia
        self.assertEqual(self.almacen_zulia.parent, self.gerencia_almacenes)
    
    def test_cross_hierarchy_queries(self):
        """Test queries across the hierarchical structure"""
        # Get all unidades under VP Operaciones
        unidades_operaciones = UnidadOrganizacional.objects.filter(
            vicepresidencia=self.vp_operaciones
        )
        self.assertEqual(unidades_operaciones.count(), 2)
        
        # Get all almacenes under gerencia
        almacenes = self.gerencia_almacenes.get_descendants()
        self.assertEqual(almacenes.count(), 1)
        self.assertEqual(almacenes.first(), self.almacen_zulia)
    
    def test_full_path_generation(self):
        """Test full path generation across all levels"""
        # The actual path includes the parent unidad in the hierarchy
        expected_path = 'Hidroven → VP Operaciones Hídricas → Gerencia de Almacenes → Almacén Regional Zulia'
        self.assertEqual(self.almacen_zulia.get_full_path(), expected_path)
    
    def test_performance_with_select_related(self):
        """Test query performance with select_related"""
        # This should generate minimal queries due to select_related
        unidades = UnidadOrganizacional.objects.select_related(
            'vicepresidencia__empresa'
        ).all()
        
        # Access related objects without additional queries
        for unidad in unidades:
            empresa_nombre = unidad.vicepresidencia.empresa.nombre
            self.assertEqual(empresa_nombre, 'Hidroven')
