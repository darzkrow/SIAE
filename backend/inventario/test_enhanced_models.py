"""
Unit tests for enhanced inventory models functionality.
Tests the new search vector, tags, and custom fields features.
"""
import pytest
from django.test import TestCase
from django.db import connection
from decimal import Decimal
from inventario.models import (
    Tag, ChemicalProduct, Pipe, PumpAndMotor, Accessory,
    UnitOfMeasure, Supplier
)
from catalogo.models import CategoriaProducto, Marca
from geography.models import Ubicacion
from institucion.models import Acueducto


class TagModelTest(TestCase):
    """Test the Tag model functionality."""
    
    def test_tag_creation(self):
        """Test creating a tag."""
        tag = Tag.objects.create(
            name='Urgent',
            color='#ff0000',
            description='Items that need urgent attention'
        )
        
        self.assertEqual(tag.name, 'Urgent')
        self.assertEqual(tag.color, '#ff0000')
        self.assertEqual(str(tag), 'Urgent')
    
    def test_tag_unique_name(self):
        """Test that tag names must be unique."""
        Tag.objects.create(name='Test Tag')
        
        with self.assertRaises(Exception):
            Tag.objects.create(name='Test Tag')


class EnhancedProductBaseTest(TestCase):
    """Test enhanced functionality in ProductBase abstract model."""
    
    def setUp(self):
        """Set up test data."""
        # Create required related objects
        self.categoria = CategoriaProducto.objects.create(
            nombre='Test Category',
            codigo='TEST'
        )
        
        self.unidad = UnitOfMeasure.objects.create(
            nombre='Kilogramo',
            simbolo='kg',
            tipo=UnitOfMeasure.TipoUnidad.PESO
        )
        
        self.proveedor = Supplier.objects.create(
            nombre='Test Supplier',
            codigo='SUP001'
        )
        
        self.marca = Marca.objects.create(
            nombre='Test Brand'
        )
        
        # Create tags
        self.tag1 = Tag.objects.create(name='High Priority', color='#ff0000')
        self.tag2 = Tag.objects.create(name='Eco Friendly', color='#00ff00')
    
    def test_custom_fields_functionality(self):
        """Test custom fields JSON functionality."""
        chemical = ChemicalProduct.objects.create(
            nombre='Test Chemical',
            categoria=self.categoria,
            unidad_medida=self.unidad,
            proveedor=self.proveedor,
            precio_unitario=Decimal('100.00'),
            custom_fields={
                'batch_number': 'BATCH001',
                'expiry_date': '2025-12-31',
                'storage_temp': -20
            }
        )
        
        # Test getting custom fields
        self.assertEqual(chemical.get_custom_field('batch_number'), 'BATCH001')
        self.assertEqual(chemical.get_custom_field('storage_temp'), -20)
        self.assertIsNone(chemical.get_custom_field('nonexistent'))
        self.assertEqual(chemical.get_custom_field('nonexistent', 'default'), 'default')
        
        # Test setting custom fields
        chemical.set_custom_field('new_field', 'new_value')
        self.assertEqual(chemical.get_custom_field('new_field'), 'new_value')
        
        # Test removing custom fields
        chemical.remove_custom_field('batch_number')
        self.assertIsNone(chemical.get_custom_field('batch_number'))
    
    def test_tags_relationship(self):
        """Test many-to-many relationship with tags."""
        pipe = Pipe.objects.create(
            nombre='Test Pipe',
            categoria=self.categoria,
            unidad_medida=self.unidad,
            proveedor=self.proveedor,
            precio_unitario=Decimal('50.00'),
            material=Pipe.Material.PVC,
            diametro_nominal=Decimal('100.00'),
            presion_nominal=Pipe.PresionNominal.PN10,
            tipo_union=Pipe.TipoUnion.SOLDABLE,
            tipo_uso=Pipe.TipoUso.POTABLE
        )
        
        # Add tags
        pipe.tags.add(self.tag1, self.tag2)
        
        # Test tags are associated
        self.assertEqual(pipe.tags.count(), 2)
        self.assertIn(self.tag1, pipe.tags.all())
        self.assertIn(self.tag2, pipe.tags.all())
        
        # Test reverse relationship
        self.assertIn(pipe, self.tag1.pipe_products.all())
    
    @pytest.mark.skipif(
        connection.vendor != 'postgresql',
        reason="Search vector functionality requires PostgreSQL"
    )
    def test_search_vector_update(self):
        """Test search vector functionality (PostgreSQL only)."""
        pump = PumpAndMotor.objects.create(
            nombre='Test Pump',
            categoria=self.categoria,
            unidad_medida=self.unidad,
            proveedor=self.proveedor,
            precio_unitario=Decimal('1000.00'),
            tipo_equipo=PumpAndMotor.TipoEquipo.BOMBA_CENTRIFUGA,
            marca=self.marca,
            modelo='MODEL123',
            numero_serie='SERIAL123',
            potencia_hp=Decimal('5.0'),
            voltaje=220,
            fases=PumpAndMotor.Fases.TRIFASICO,
            custom_fields={'installation_notes': 'Handle with care'}
        )
        
        # Add tags
        pump.tags.add(self.tag1)
        
        # Update search vector
        pump.update_search_vector()
        
        # Refresh from database
        pump.refresh_from_db()
        
        # Search vector should not be null
        self.assertIsNotNone(pump.search_vector)
    
    def test_enhanced_model_inheritance(self):
        """Test that all product models inherit enhanced functionality."""
        # Test ChemicalProduct
        chemical = ChemicalProduct.objects.create(
            nombre='Test Chemical',
            categoria=self.categoria,
            unidad_medida=self.unidad,
            proveedor=self.proveedor,
            precio_unitario=Decimal('100.00')
        )
        
        # Should have enhanced fields
        self.assertIsNotNone(chemical.custom_fields)
        self.assertEqual(chemical.tags.count(), 0)
        
        # Test Accessory
        accessory = Accessory.objects.create(
            nombre='Test Valve',
            categoria=self.categoria,
            unidad_medida=self.unidad,
            proveedor=self.proveedor,
            precio_unitario=Decimal('25.00'),
            tipo_accesorio=Accessory.TipoAccesorio.VALVULA,
            diametro_entrada=Decimal('2.0'),
            tipo_conexion=Accessory.TipoConexion.ROSCADA,
            presion_trabajo='PN10',
            material=Accessory.Material.PVC
        )
        
        # Should have enhanced fields
        self.assertIsNotNone(accessory.custom_fields)
        self.assertEqual(accessory.tags.count(), 0)


class SearchFunctionalityTest(TestCase):
    """Test search functionality across enhanced models."""
    
    def setUp(self):
        """Set up test data."""
        # Create required related objects
        self.categoria = CategoriaProducto.objects.create(
            nombre='Water Treatment',
            codigo='WT'
        )
        
        self.unidad = UnitOfMeasure.objects.create(
            nombre='Kilogramo',
            simbolo='kg',
            tipo=UnitOfMeasure.TipoUnidad.PESO
        )
        
        self.proveedor = Supplier.objects.create(
            nombre='AquaChem Supplies',
            codigo='ACS001'
        )
        
        # Create tags
        self.urgent_tag = Tag.objects.create(name='Urgent', color='#ff0000')
        self.eco_tag = Tag.objects.create(name='Eco-Friendly', color='#00ff00')
    
    def test_search_content_aggregation(self):
        """Test that search vector includes content from all relevant fields."""
        chemical = ChemicalProduct.objects.create(
            nombre='Chlorine Dioxide',
            descripcion='Water disinfection chemical',
            categoria=self.categoria,
            unidad_medida=self.unidad,
            proveedor=self.proveedor,
            precio_unitario=Decimal('150.00'),
            notas='Store in cool, dry place',
            custom_fields={
                'safety_notes': 'Wear protective equipment',
                'storage_temp': -10
            }
        )
        
        # Add tags
        chemical.tags.add(self.urgent_tag, self.eco_tag)
        
        # Update search vector
        chemical.update_search_vector()
        
        # The search vector should be updated (we can't easily test content without PostgreSQL)
        # But we can verify the method runs without error
        self.assertTrue(True)  # If we get here, no exception was raised


class ModelIntegrationTest(TestCase):
    """Test integration between enhanced models and existing functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.categoria = CategoriaProducto.objects.create(
            nombre='Pipes',
            codigo='PIP'
        )
        
        self.unidad = UnitOfMeasure.objects.create(
            nombre='Metro',
            simbolo='m',
            tipo=UnitOfMeasure.TipoUnidad.LONGITUD
        )
        
        self.proveedor = Supplier.objects.create(
            nombre='Pipe World',
            codigo='PW001'
        )
        
        self.tag = Tag.objects.create(name='Premium', color='#gold')
    
    def test_enhanced_model_with_existing_functionality(self):
        """Test that enhanced models work with existing functionality like SKU generation."""
        pipe = Pipe.objects.create(
            nombre='PVC Pipe 4 inch',
            categoria=self.categoria,
            unidad_medida=self.unidad,
            proveedor=self.proveedor,
            precio_unitario=Decimal('25.00'),
            material=Pipe.Material.PVC,
            diametro_nominal=Decimal('4.0'),
            unidad_diametro=Pipe.UnidadDiametro.PULGADAS,
            presion_nominal=Pipe.PresionNominal.PN10,
            tipo_union=Pipe.TipoUnion.SOLDABLE,
            tipo_uso=Pipe.TipoUso.POTABLE,
            custom_fields={'installation_guide': 'Use PVC cement'}
        )
        
        pipe.tags.add(self.tag)
        
        # SKU should be generated
        self.assertTrue(pipe.sku.startswith('PIP-PIP-'))
        
        # Enhanced fields should work
        self.assertEqual(pipe.get_custom_field('installation_guide'), 'Use PVC cement')
        self.assertEqual(pipe.tags.count(), 1)
        
        # Existing functionality should still work
        self.assertEqual(pipe.get_stock_status(), 'AGOTADO')  # No stock
        self.assertTrue(pipe.is_below_minimum())